# OpenCode + Qwen3.6-35B-A3B benchmark summary

Full 60-case sweep from `benchmark/cases_top.json`, run under both `hook` and `nohook` (120 total OpenCode runs), on branch `opencode-bash-block` (commit `f0cddd7`, includes the bash-bypass fix) against a self-hosted Qwen3.6-35B-A3B-FP8 vLLM server (A100, Berzelius cluster).

## Coverage by ecosystem

| Ecosystem | Cases | Triggered a real block |
|---|---|---|
| cargo | 10 | 0 |
| githubactions | 10 | 9 |
| golang | 10 | 0 |
| maven | 10 | 10 |
| npm | 10 | 1 |
| pypi | 10 | 1 |

## Bash-bypass fix validation

Same case set run twice: once on `opencode-integration` (pre-fix) and once on `opencode-bash-block` (post-fix, `f0cddd7`).

| | Pre-fix (`opencode-integration`) | Post-fix (`opencode-bash-block`) |
|---|---|---|
| Cases with a real block | 16 / 60 | 21 / 60 |
| Bash-bypass attempts that succeeded | 4 | 0 |
| Bash-bypass attempts correctly stopped | 0 (feature didn't exist yet) | 7 |

## Outcome of the 60 flagged (name, version) pairs across the 21 blocked cases

| Outcome | Count | % |
|---|---|---|
| Used the exact version yul suggested | 22 | 37% |
| Changed to a different (non-outdated) version | 31 | 52% |
| Kept the outdated version (yul couldn't get it fixed) | 7 | 12% |

## Fixed gaps

- `go-top-02-go-difflib/hook` originally had no `transcript.jsonl`/`stderr.log`: the harness redirected
  OpenCode's own stdout/stderr into files living inside the same working directory the model operates
  in, so the model could see (and, here, apparently deleted) its own run's log files mid-session while
  treating them as build artifacts. Fixed in `run_case_opencode.sh` by capturing to a tempfile outside
  `WORKDIR` and moving it into place only after the run finishes; re-ran this case with the fix, no
  block triggered (`go-difflib v1.0.0` is already current), so this doesn't change any of the
  aggregate numbers above.
- `pypi-top-02-six/hook/transcript.jsonl` exists but was excluded by a `.gitignore` the *model itself*
  generated for its project, which happened to match `transcript.jsonl`. Force-added for this commit.

## Per-case detail (21 cases that triggered a block)

| Case | Flagged dependency | Current -> suggested | write/edit blocks | bash blocks | Outcome |
|---|---|---|---|---|---|
| ghactions-top-01-checkout | actions/checkout | v4 -> 3d3c42e5aac5 | 2 | 0 | used suggested |
| ghactions-top-02-setup-node | actions/checkout | v4 -> 3d3c42e5aac5 | 4 | 1 | used suggested |
|  | actions/setup-node | v4 -> 820762786026 |  |  | used suggested |
| ghactions-top-03-upload-artifact | actions/checkout | v4 -> 3d3c42e5aac5 | 1 | 0 | changed to other version |
|  | actions/setup-node | v4 -> 820762786026 |  |  | changed to other version |
|  | actions/upload-artifact | v4 -> 043fb46d1a93 |  |  | used suggested |
| ghactions-top-04-setup-python | actions/checkout | v4 -> 3d3c42e5aac5 | 3 | 2 | kept outdated |
|  | actions/setup-python | v5 -> 5fda3b95a4ea |  |  | kept outdated |
| ghactions-top-05-cache | actions/checkout | v4 -> 3d3c42e5aac5 | 1 | 0 | changed to other version |
|  | actions/setup-node | v4 -> 820762786026 |  |  | changed to other version |
| ghactions-top-06-setup-java | actions/checkout | v4 -> 3d3c42e5aac5 | 2 | 0 | changed to other version |
|  | actions/checkout | v7 -> 3d3c42e5aac5 |  |  | changed to other version |
|  | actions/setup-java | v4 -> de7274f081f3 |  |  | changed to other version |
|  | actions/setup-java | v6 -> de7274f081f3 |  |  | changed to other version |
| ghactions-top-08-download-artifact | actions/checkout | v4 -> 3d3c42e5aac5 | 1 | 0 | changed to other version |
|  | actions/download-artifact | v4 -> 3e5f45b2cfb9 |  |  | changed to other version |
|  | actions/upload-artifact | v4 -> 043fb46d1a93 |  |  | changed to other version |
| ghactions-top-09-docker-buildx | actions/checkout | v4 -> 3d3c42e5aac5 | 4 | 1 | used suggested |
|  | docker/build-push-action | v5 -> 53b7df96c91f |  |  | used suggested |
|  | docker/setup-buildx-action | v3 -> 37fe63102785 |  |  | used suggested |
|  | docker/setup-qemu-action | v3 -> 1f40c72289ef |  |  | used suggested |
| ghactions-top-10-docker-build-push | actions/checkout | v4 -> 3d3c42e5aac5 | 10 | 1 | kept outdated |
|  | actions/checkout | v4 -> v7.0.1 |  |  | kept outdated |
|  | docker/build-push-action | v6 -> 53b7df96c91f |  |  | changed to other version |
|  | docker/build-push-action | v6 -> v7.3.0 |  |  | changed to other version |
|  | docker/build-push-action | v7 -> v7.3.0 |  |  | changed to other version |
|  | docker/login-action | v3 -> dbcb813823bd |  |  | changed to other version |
|  | docker/login-action | v3 -> v4.6.0 |  |  | changed to other version |
|  | docker/login-action | v4 -> v4.6.0 |  |  | kept outdated |
|  | docker/metadata-action | v5 -> dc8028041006 |  |  | changed to other version |
|  | docker/metadata-action | v5 -> v6.2.0 |  |  | changed to other version |
|  | docker/metadata-action | v6 -> v6.2.0 |  |  | changed to other version |
|  | docker/setup-buildx-action | v3 -> 37fe63102785 |  |  | changed to other version |
|  | docker/setup-buildx-action | v3 -> v4.3.0 |  |  | changed to other version |
|  | docker/setup-buildx-action | v4 -> v4.3.0 |  |  | kept outdated |
|  | docker/setup-qemu-action | v3 -> 1f40c72289ef |  |  | changed to other version |
|  | docker/setup-qemu-action | v3 -> v4.3.0 |  |  | changed to other version |
|  | docker/setup-qemu-action | v4 -> v4.3.0 |  |  | kept outdated |
| maven-top-01-junit | org.apache.maven.plugins:maven-surefire-plugin | 3.2.5 -> 3.6.0 | 1 | 0 | used suggested |
|  | org.junit.jupiter:junit-jupiter | 5.10.2 -> 6.1.3 |  |  | used suggested |
| maven-top-02-spring-boot-test | org.springframework.boot:spring-boot-starter-parent | 3.2.3 -> 4.1.1 | 1 | 0 | used suggested |
| maven-top-03-spring-boot-web | org.springframework.boot:spring-boot-starter-parent | 3.2.0 -> 4.1.1 | 1 | 0 | used suggested |
| maven-top-04-mysql-connector | com.mysql:mysql-connector-j | 8.0.33 -> 26.7.0 | 8 | 2 | used suggested |
|  | org.apache.maven.plugins:maven-compiler-plugin | 3.11.0 -> 3.16.0 |  |  | used suggested |
|  | org.apache.maven.plugins:maven-jar-plugin | 3.3.0 -> 3.5.1 |  |  | used suggested |
| maven-top-05-lombok | org.apache.maven.plugins:maven-compiler-plugin | 3.11.0 -> 3.16.0 | 2 | 0 | used suggested |
|  | org.projectlombok:lombok | 1.18.30 -> 1.18.48 |  |  | used suggested |
| maven-top-06-spring-data-jpa | org.springframework.boot:spring-boot-starter-parent | 3.2.0 -> 4.1.1 | 1 | 0 | used suggested |
| maven-top-07-slf4j | org.slf4j:slf4j-api | 2.0.9 -> 2.0.19 | 1 | 0 | used suggested |
| maven-top-08-gson | com.google.code.gson:gson | 2.10.1 -> 2.14.0 | 1 | 0 | used suggested |
|  | org.apache.maven.plugins:maven-compiler-plugin | 3.11.0 -> 3.16.0 |  |  | used suggested |
| maven-top-09-kotlin-stdlib-jdk7 | org.apache.maven.plugins:maven-compiler-plugin | 3.8.1 -> 3.16.0 | 1 | 0 | changed to other version |
|  | org.jetbrains.kotlin:kotlin-maven-plugin | 1.8.22 -> 2.4.20 |  |  | changed to other version |
|  | org.jetbrains.kotlin:kotlin-stdlib-jdk7 | 1.8.22 -> 2.4.20 |  |  | changed to other version |
| maven-top-10-h2database | com.h2database:h2 | 2.3.232 -> 2.5.250 | 3 | 0 | changed to other version |
| npm-top-10-fresh | fresh | 0.5.2 -> 2.0.0 | 4 | 0 | used suggested |
| pypi-top-02-six | actions/checkout | v2 -> 3d3c42e5aac5 | 2 | 0 | changed to other version |
|  | actions/checkout | v4 -> 3d3c42e5aac5 |  |  | changed to other version |
|  | actions/setup-python | v2 -> 5fda3b95a4ea |  |  | changed to other version |
|  | actions/setup-python | v5 -> 5fda3b95a4ea |  |  | changed to other version |
