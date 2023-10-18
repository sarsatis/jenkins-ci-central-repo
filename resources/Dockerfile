# Stage 1: Build the application with Gradle
# FROM gradle AS builder
# WORKDIR /app
# COPY build.gradle settings.gradle ./
# COPY src ./src
# RUN gradle build -x test --no-daemon

# Stage 2: Create the final image with OpenJDK 17 and Gradle 8.3
# FROM khipu/openjdk17-alpine:latest
# WORKDIR /app
# COPY --from=builder /app/build/libs/employeemanagement-0.0.1-SNAPSHOT.jar ./app.jar
# EXPOSE 8080
# CMD ["java", "-jar", "app.jar"]


FROM khipu/openjdk17-alpine:latest
VOLUME /tmp
EXPOSE 8080
ARG NAME=default

COPY /build/libs/$NAME-0.0.1-SNAPSHOT.jar app.jar

ENTRYPOINT ["java","-jar","/app.jar"]