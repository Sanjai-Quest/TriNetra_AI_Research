package ai.trinetra.evidence.service;

import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import io.minio.BucketExistsArgs;
import io.minio.MakeBucketArgs;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.util.UUID;

/**
 * Phase 3 hardened MinioStorageService.
 *
 * Changes from Phase 2:
 * 1. @CircuitBreaker + @Retry on uploadFile (instance "minioUpload")
 * 2. Fallback on upload failure: log + throw EvidenceStorageException
 * 3. Micrometer counter for upload success/failure
 * 4. Timer for upload duration
 * 5. Init failure is now fatal (throws EvidenceInitException) so startup fails fast
 *    rather than silently operating with no MinIO client
 */
@Service
@Slf4j
public class MinioStorageService {

    @Value("${minio.endpoint}")
    private String endpoint;

    @Value("${minio.access-key}")
    private String accessKey;

    @Value("${minio.secret-key}")
    private String secretKey;

    @Value("${minio.bucket-name}")
    private String bucketName;

    private MinioClient minioClient;

    private final Counter uploadsSucceededCounter;
    private final Counter uploadsFailedCounter;
    private final Timer uploadDurationTimer;

    public MinioStorageService(MeterRegistry registry) {
        this.uploadsSucceededCounter = Counter.builder("trinetra.evidence.uploads.succeeded")
                .description("Evidence files successfully uploaded to MinIO")
                .tag("service", "evidence-service")
                .register(registry);
        this.uploadsFailedCounter = Counter.builder("trinetra.evidence.uploads.failed")
                .description("Evidence file upload failures")
                .tag("service", "evidence-service")
                .register(registry);
        this.uploadDurationTimer = Timer.builder("trinetra.evidence.upload.duration")
                .description("Time taken to upload evidence files to MinIO")
                .tag("service", "evidence-service")
                .publishPercentiles(0.5, 0.95, 0.99)
                .register(registry);
    }

    @PostConstruct
    public void init() {
        try {
            minioClient = MinioClient.builder()
                    .endpoint(endpoint)
                    .credentials(accessKey, secretKey)
                    .build();

            boolean exists = minioClient.bucketExists(BucketExistsArgs.builder().bucket(bucketName).build());
            if (!exists) {
                minioClient.makeBucket(MakeBucketArgs.builder().bucket(bucketName).build());
                log.info("[evidence-service] MinIO bucket created: {}", bucketName);
            } else {
                log.info("[evidence-service] MinIO connected, bucket exists: {}", bucketName);
            }
        } catch (Exception e) {
            // Phase 3: fail fast — don't silently operate without MinIO
            log.error("[evidence-service] MinIO initialization FAILED: {}", e.getMessage());
            throw new IllegalStateException("MinIO initialization failed. Check MINIO_ENDPOINT and credentials.", e);
        }
    }

    @CircuitBreaker(name = "minioUpload", fallbackMethod = "uploadFileFallback")
    @Retry(name = "minioUpload")
    public String uploadFile(UUID claimId, UUID evidenceId, MultipartFile file) throws Exception {
        String objectKey = String.format("claims/%s/evidence/%s/%s", claimId, evidenceId, file.getOriginalFilename());

        uploadDurationTimer.record(() -> {
            try (InputStream is = file.getInputStream()) {
                minioClient.putObject(
                        PutObjectArgs.builder()
                                .bucket(bucketName)
                                .object(objectKey)
                                .stream(is, file.getSize(), -1)
                                .contentType(file.getContentType())
                                .build()
                );
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        });

        uploadsSucceededCounter.increment();
        log.info("[evidence-service] file.uploaded claimId={} evidenceId={} key={}", claimId, evidenceId, objectKey);
        return String.format("%s/%s/%s", endpoint, bucketName, objectKey);
    }

    /** Fallback: MinIO circuit is open or retries exhausted */
    public String uploadFileFallback(UUID claimId, UUID evidenceId, MultipartFile file, Throwable t) {
        uploadsFailedCounter.increment();
        log.error("[evidence-service] MinIO CIRCUIT OPEN — upload failed. claimId={} evidenceId={} reason={}",
                claimId, evidenceId, t.getMessage());
        throw new RuntimeException("Evidence storage temporarily unavailable. Please retry in 30 seconds.");
    }
}
