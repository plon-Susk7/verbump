echo "COMMIT_FILES_MAP=$(jq -n --argjson commits "${{ toJson(github.event.commits) }}" '
$commits | map({message: .message, files: .added + .modified + .removed})')"
