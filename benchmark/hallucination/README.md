# hallucination benchmark

A deterministic precision/recall harness for yul's Maven hallucination
check (`pkg/maven` `ExistenceChecker`). Unlike the `claude -p` benchmark in
the parent directory, this one does not invoke a model - it feeds crafted
`PreToolUse` payloads straight to the `yul` binary and inspects stderr.

## Run

```sh
./run.sh                 # builds ./ and runs
./run.sh /path/to/yul    # test a specific binary
YUL_BENCH_DELAY=0.5 ./run.sh   # slower, gentler on the network
```

Exit 0 and `OK` means every real dependency was left alone and every fake
one was reported with the right kind of hallucination.

## What it measures

For each fixture it adds one `<dependency>` to a fresh `pom.xml` and checks
what yul's stderr says:

| `label`        | expectation                            |
| -------------- | -------------------------------------- |
| `real`         | not reported hallucinated              |
| `fake-package` | reported `hallucinated package`        |
| `fake-version` | reported `hallucinated version`        |

A `real` fixture pinned to an old-but-genuine version (`real-guava-old-version`,
`guava:18.0`) still *blocks* - on the separate outdated-version check - and
that is not counted as a false positive, because the harness classifies on
the stderr reason, not the exit code.

## Fixtures

`fixtures.jsonl`, one JSON object per line:

```json
{"id": "...", "group": "...", "artifact": "...", "version": "...", "label": "real|fake-package|fake-version"}
```

Hand-built, not sampled from real transcripts.

- `fake-package`: a real groupId with a wrong artifactId
  (`org.slf4j:slf4j-core`), an invented submodule
  (`jackson-databind-blackbird`), the wrong groupId for a real library
  (`com.squareup.retrofit:retrofit-gson`). Each 404s at
  `https://repo1.maven.org/maven2/<group as path>/<artifact>/maven-metadata.xml`.
- `fake-version`: a real coordinate at a version absent from that file's
  `<versioning><versions>` list (`com.google.guava:guava:999.0-jre`).

## Network

The check GETs `maven-metadata.xml` off `repo1.maven.org` (a static CDN);
the 200/404 and the version list it carries are reproducible. Any other
status, a transport error, unparseable XML, or an empty version list makes
yul fail open, which the harness flags as a missed fake (`WARN` / exit 1)
rather than passing silently.
