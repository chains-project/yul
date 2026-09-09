# BUMP 50-case survey

50 cases from chains-project/bump, each: extract the `-pre` project,
prompt Claude with "Upgrade the `<group>:<artifact>` dependency in this
project." (no "latest"/"outdated" wording), once under the yul
`PreToolUse`+`SessionStart` hook and once with no hook, from the same
extracted source.

- Extraction failed entirely (docker pull/cp) for 0/50 cases.
- yul flagged something during the `hook` run for 13/50 cases.

| id | project | dependency | before | hook: after | hook: yul | nohook: after |
|---|---|---|---|---|---|---|
| 00a7cc31-mina-core | quickfixj | org.apache.mina:mina-core | 2.1.5 | 2.2.4 | none | 2.2.9 |
| 02363207-slf4j-api | recheck | org.slf4j:slf4j-api | 1.7.36 | 2.0.19 | outdated-flagged-somewhere | 2.0.17 |
| 02eedffd-spring-core | IDS-Messaging-Services | org.springframework:spring-core | 5.3.24 | 7.0.8 | none | 5.3.39 |
| 01609f96-spring-core | IDS-Messaging-Services | org.springframework:spring-core | 5.3.24 | 7.0.9 | outdated-flagged-somewhere | 5.3.39 |
| 01737a78-google-cloud-shared-dependencies | java-storage-nio | com.google.cloud:google-cloud-shared-dependencies | 3.11.0 | 3.67.0 | outdated-flagged-somewhere | 3.63.0 |
| 04c07b06-slf4j-api | pdb | org.slf4j:slf4j-api | 1.7.36 | 2.0.16 | none | 2.0.17 |
| 0305beaf-mysql-connector-java | pdb | mysql:mysql-connector-java | 5.1.49 | 8.0.33 | none | 8.0.33 |
| 063cf862-jackson-databind | wsdoc | com.fasterxml.jackson.core:jackson-databind | 2.4.2 | 2.22.2 | outdated-flagged-somewhere | 2.19.0 |
| 04f776fa-gax | snowflake-jdbc | com.google.api:gax | 2.16.0 | 2.85.0 | outdated-flagged-somewhere | 2.81.0 |
| 00c78c12-bom-2.289.x | publish-over-ssh-plugin | io.jenkins.tools.bom:bom-2.289.x | 961.vf0c9f6f59827 | 962.vf0c9f6f59827 (⏱ timed out) | none | 1500.ve4d05cd32975 |
| 072528ee-slf4j-api | sign-maven-plugin | org.slf4j:slf4j-api | 1.7.36 | 2.0.19 | outdated-flagged-somewhere | 2.0.17 |
| 0771fe8d-checkstyle | opennlp | com.puppycrawl.tools:checkstyle | 7.2 | 7.2 | none | 7.2 |
| 067f5d2c-libthrift | singer | org.apache.thrift:libthrift | 0.12.0 | 0.23.0 | none | ${thrift.version} |
| 0671a30e-junit-platform-surefire-provider | IDS-Messaging-Services | org.junit.platform:junit-platform-surefire-provider | 1.0.3 | 1.3.2 | none | 1.3.2 |
| 07fad972-logback-classic | pay-adminusers | ch.qos.logback:logback-classic | 1.2.11 | 1.5.19 | none | 1.5.18 |
| 07ff1a34-spring-context | camunda-platform-7-mockito | org.springframework:spring-context | 5.3.23 | 5.3.39 | none | 5.3.39 |
| 0968864d-assertj-core | assertj-guava | org.assertj:assertj-core | 3.22.0 | 3.27.7 | outdated-flagged-somewhere | 3.27.3 |
| 097d93fb-poi-ooxml | fscrawler | org.apache.poi:poi-ooxml | 4.1.2 | 5.5.1 | outdated-flagged-somewhere | 5.5.1 |
| 06c53868-acceptance-test-harness | code-coverage-api-plugin | org.jenkins-ci:acceptance-test-harness | 5504.v485694f31cdf | 5504.v485694f31cdf (⏱ timed out) | none | 5504.v485694f31cdf (⏱ timed out) |
| 08e33c7b-spring-webmvc | IDS-Messaging-Services | org.springframework:spring-webmvc | 5.3.24 | 6.2.8 | none | 5.3.39 |
| 09a8774f-echarts-api | pull-request-monitoring-plugin | io.jenkins.plugins:echarts-api | 5.1.2-3 | 5.4.0-1 | none | 6.1.0-1306.vcee1648c16a_4 |
| 07e4b289-acceptance-test-harness | code-coverage-api-plugin | org.jenkins-ci:acceptance-test-harness | 5588.vd13b_52985008 | 5588.vd13b_52985008 (⏱ timed out) | none | 6724.va_7c5c4b_fcf9c |
| 0a11c040-snakeyaml | simplelocalize-cli | org.yaml:snakeyaml | 1.24 | 2.3 | none | 2.4 |
| 0abf7148-jasperreports | biapi | net.sf.jasperreports:jasperreports | 6.18.1 | 7.0.8 | outdated-flagged-somewhere | 7.0.3 |
| 0c748afc-jackson-databind | dropwizard-pac4j | com.fasterxml.jackson.core:jackson-databind | 2.10.5.1 | 2.22.2 | none | 2.22.2 |
| 0c088ff4-js-scriptengine | a | org.graalvm.js:js-scriptengine | 22.3.2 | 24.2.1 | none | 24.2.1 |
| 0c9a9c80-google-cloud-shared-dependencies | java-pubsub-group-kafka-connector | com.google.cloud:google-cloud-shared-dependencies | 3.6.0 | 3.67.0 | outdated-flagged-somewhere | 3.63.0 |
| 0cdcc1f1-spring-core | LPVS | org.springframework:spring-core | 5.3.23 | 5.3.39 | none | 5.3.39 |
| 0ddd0efa-spring-boot-starter | IDS-Messaging-Services | org.springframework.boot:spring-boot-starter | 2.7.5 | 3.3.4 | none | 3.5.3 |
| 0e8625f4-jetty-server | jadler | org.eclipse.jetty:jetty-server | 8.1.11.v20130520 | 12.0.9 | none | 8.1.22.v20160922 |
| 0c60d0b0-spring-web | IDS-Messaging-Services | org.springframework:spring-web | 5.3.24 | 5.3.31 (⏱ timed out) | outdated-flagged-somewhere | 5.3.39 |
| 0ed34fa6-spring-context | camunda-platform-7-mockito | org.springframework:spring-context | 5.3.23 | 6.1.13 | none | 6.2.8 |
| 0ee8b937-mockito-core | junit-quickcheck | org.mockito:mockito-core | 4.11.0 | 5.14.2 | none | 4.11.0 |
| 1053033e-commons-io | jcabi-maven-plugin | commons-io:commons-io | 2.11.0 | 2.22.0 | outdated-flagged-somewhere | 2.22.0 |
| 115827c6-jakarta.servlet-api | dropwizard-pac4j | jakarta.servlet:jakarta.servlet-api | 4.0.4 | 6.1.0 | none | 4.0.4 |
| 10d7545c-dropwizard-client | lithium | io.dropwizard:dropwizard-client | 2.1.5 | 2.1.12 | none | 2.1.12 |
| 0ec1ab7e-relaxng-datatype | causeway | com.sun.xml.bind.external:relaxng-datatype | 2.3.6 | 4.0.6 | none | 4.0.6 |
| 11c09e31-spring-context | camunda-platform-7-mockito | org.springframework:spring-context | 5.3.23 | 5.3.39 | none | 5.3.39 |
| 11be71ab-spring-context | camunda-platform-7-mockito | org.springframework:spring-context | 5.3.23 | 6.2.8 | none | 5.3.39 |
| 11fa4228-jackson-databind | IDS-Messaging-Services | com.fasterxml.jackson.core:jackson-databind | 2.9.10.8 | 2.22.2 | none | 2.19.0 |
| 12684ee6-commons-io | cucumber-reporting | commons-io:commons-io | 2.7 | 2.19.0 | none | 2.22.0 |
| 125f1253-plexus-utils | jspc-maven-plugin | org.codehaus.plexus:plexus-utils | 3.5.1 | 4.1.0 | none | 3.6.0 |
| 1266a8c8-slf4j-api | pay-adminusers | org.slf4j:slf4j-api | 1.7.36 | 2.0.16 | none | 2.0.17 |
| 12e23771-h2 | geostore | com.h2database:h2 | 1.3.175 | 2.3.232 | none | 2.3.232 |
| 13fd75e2-asto-core | docker-adapter | com.artipie:asto-core | v1.13.0 | v1.17.16 | none | v1.17.16 |
| 14e2c8d4-slf4j-api | pay-adminusers | org.slf4j:slf4j-api | 1.7.36 | 2.0.19 | outdated-flagged-somewhere | 2.0.17 |
| 12830c4f-rngom | causeway | com.sun.xml.bind.external:rngom | 2.3.6 | 2.3.7 | none | 4.0.6 |
| 14fc5fa6-flyway-core | nem | org.flywaydb:flyway-core | 3.2.1 | 11.8.2 | none | 11.8.2 |
| 14270a2f-commons-text-api | forensics-api-plugin | io.jenkins.plugins:commons-text-api | 1.10.0-27.vb_fa_3896786a_7 | 1.15.0-218.va_61573470393 | none | 1.15.0-218.va_61573470393 |
| 1280336e-bom-2.277.x | config-file-provider-plugin | io.jenkins.tools.bom:bom-2.277.x | 29 | 29 (⏱ timed out) | none | 29 (⏱ timed out) |
