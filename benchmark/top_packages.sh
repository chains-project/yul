#!/bin/bash
#
# Fetches the top N packages (by a given ecosyste.ms popularity metric) for
# every package ecosystem that yul supports, provided ecosyste.ms also
# supports it. Modeled on the collection phase of
# https://github.com/chains-project/zkSBOM/blob/main/rq3/go/pipeline.sh
#
# Output is package names only, grouped per ecosystem - useful as raw
# material for picking benchmark/cases.json candidates, not a finished
# dataset.

## CLI
COUNT="${1:-10}"
METRIC="${2:-dependent_repos_count}"

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
	echo 'USAGE:   ./top_packages.sh [COUNT] [METRIC]'
	echo 'EXAMPLE: ./top_packages.sh 10 dependent_repos_count'
	echo ''
	echo '- COUNT defaults to 10'
	echo '- METRIC is any sort field the ecosyste.ms package_names endpoint'
	echo "  accepts (e.g. 'downloads', 'dependent_repos_count',"
	echo "  'docker_downloads_count'); defaults to 'dependent_repos_count'"
	echo "  since it is populated across every ecosystem below, unlike"
	echo "  'downloads' which only makes sense for a registry that tracks it."
	exit 0
fi

MAX_TRIES=100

# yul-supported-manifest -> ecosyste.ms ecosystem key (packages.ecosyste.ms
# groups registries by an `ecosystem` field; the registry `name` itself -
# e.g. "npmjs.org", "pypi.org", "proxy.golang.org" - is an implementation
# detail that has changed before, so it's resolved by ecosystem, not
# hardcoded).
declare -A ECOSYSTEMS=(
	[maven]="maven"
	[pypi]="pypi"
	[npm]="npm"
	[githubactions]="actions"
	[go]="go"
	[cargo]="cargo"
)

## Helpers
# urlencode STRING: percent-encode a single URL path segment (registry
# names like "github actions" contain spaces).
urlencode() {
	jq -rn --arg s "$1" '$s|@uri'
}

# fetch URL <max_tries>: curl the URL, retrying on non-JSON / error
# responses. Prints the raw response body on success, nothing on failure.
fetch() {
	local url="$1"
	local response
	for ((attempt = 1; attempt <= MAX_TRIES; attempt++)); do
		response=$(curl -sX 'GET' "${url}" -H 'accept: application/json')
		if echo "${response}" | jq -e 'type=="array" or type=="object"' >/dev/null 2>&1; then
			printf '%s' "${response}"
			return 0
		fi
		echo "    ! bad response (attempt ${attempt}/${MAX_TRIES}) on: ${url}" 1>&2
		[[ ${attempt} -lt ${MAX_TRIES} ]] && sleep 2
	done
	return 1
}

## Main
echo "Resolving ecosyste.ms registries for yul-supported ecosystems ..."
declare -A REGISTRY
for eco in "${!ECOSYSTEMS[@]}"; do
	ecosystem_key="${ECOSYSTEMS[${eco}]}"
	body=$(fetch "https://packages.ecosyste.ms/api/v1/registries") || {
		echo "  ! could not list registries, giving up entirely" 1>&2
		exit 1
	}
	name=$(echo "${body}" | jq -er --arg eco "${ecosystem_key}" \
		'[.[] | select(.ecosystem == $eco)] | sort_by(-(.packages_count // 0)) | .[0].name')
	if [[ -z "${name}" || "${name}" == "null" ]]; then
		echo "  ! no ecosyste.ms registry found for ecosystem '${ecosystem_key}' (yul: ${eco}), skipping"
		continue
	fi
	echo "  ${eco} (${ecosystem_key}) -> registry '${name}'"
	REGISTRY[${eco}]="${name}"
done

echo ''
echo "== TOP ${COUNT} PACKAGES PER ECOSYSTEM (sorted by '${METRIC}') =="
for eco in "${!REGISTRY[@]}"; do
	registry="${REGISTRY[${eco}]}"
	echo ''
	echo "-- ${eco} (registry: ${registry}) --"

	url="https://packages.ecosyste.ms/api/v1/registries/$(urlencode "${registry}")/package_names?page=1&per_page=${COUNT}&sort=${METRIC}"
	body=$(fetch "${url}") || {
		echo "  ! giving up on ${eco}" 1>&2
		continue
	}
	echo "${body}" | jq -er 'if type=="array" then .[] else error("not an array") end' 2>/dev/null \
		| sed 's/^/  /'
done
