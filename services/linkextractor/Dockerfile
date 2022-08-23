#
# Build stage
#
FROM maven:3.8.6-openjdk-18-slim AS build
COPY src /home/app/src
COPY pom.xml /home/app
RUN mvn -f /home/app/pom.xml clean package

#
# Package stage
#
FROM openjdk:18-jdk-slim
COPY --from=build /home/app/target/linkextractor-1.0-shaded.jar /home/app/linkextractor.jar
EXPOSE 80
WORKDIR /home/app
ENTRYPOINT ["java","-jar","/home/app/linkextractor.jar"]
