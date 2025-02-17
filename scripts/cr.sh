#!/bin/bash

# Constants
CR_BASE_DIR="docs/implementation/changes"
TEMPLATE_PATH="$CR_BASE_DIR/CHANGE_REQUEST_TEMPLATE.md"

# Function to get CR directory based on status
get_cr_dir() {
    local status="$1"
    case "$status" in
        "backlog") echo "$CR_BASE_DIR/1-backlog" ;;
        "sprint-backlog") echo "$CR_BASE_DIR/2-sprint-backlog" ;;
        "in-progress") echo "$CR_BASE_DIR/3-in-progress" ;;
        "in-review") echo "$CR_BASE_DIR/4-in-review" ;;
        "done")
            local year=$(date +%Y)
            local month=$(date +%m)
            echo "$CR_BASE_DIR/5-done/$year/$month"
            ;;
        *) echo "Invalid status: $status" >&2; exit 1 ;;
    esac
}

# Function to move CR file
move_cr() {
    local cr_number="$1"
    local new_status="$2"
    local current_file=$(find "$CR_BASE_DIR" -name "$cr_number.md")

    if [ -z "$current_file" ]; then
        echo "CR file not found: $cr_number.md"
        exit 1
    }

    local target_dir=$(get_cr_dir "$new_status")
    mkdir -p "$target_dir"
    mv "$current_file" "$target_dir/"

    # Update status in CR file
    sed -i '' "s/^- \*\*Status\*\*: .*/- **Status**: ${new_status^}/" "$target_dir/$cr_number.md"

    # Add status history entry
    local date=$(date +%Y-%m-%d)
    sed -i '' "/^| Date | Status | Notes |/a\\
| $date | ${new_status^} | $3 |" "$target_dir/$cr_number.md"
}

# Function to create a new CR
create_cr() {
    local title="$1"
    local description="$2"
    local type="$3"
    local today=$(date +%Y.%m)
    local year=$(date +%Y)
    local month=$(date +%m)

    # Create GitHub issue
    echo "Creating GitHub issue..."
    issue_number=$(gh issue create --title "$title" --body "$description" --label "$type" --json number --jq '.number')

    # Create branch
    echo "Creating branch..."
    git checkout -b "feature/$issue_number-${title// /-}"

    # Create CR document
    echo "Creating CR document..."
    cr_number="CR-$today-$issue_number"
    target_dir=$(get_cr_dir "backlog")
    mkdir -p "$target_dir"

    cp "$TEMPLATE_PATH" "$target_dir/$cr_number.md"

    # Update CR information
    sed -i '' "s/CR-YYYY.MM-N/$cr_number/" "$target_dir/$cr_number.md"
    sed -i '' "s/#N/#$issue_number/" "$target_dir/$cr_number.md"
    sed -i '' "s/Brief descriptive title/$title/" "$target_dir/$cr_number.md"
    sed -i '' "s/\[Feature | Bugfix | Refactor | Documentation\]/${type^}/" "$target_dir/$cr_number.md"
    sed -i '' "s/\[Backlog | Sprint Backlog | In Progress | In Review | Done\]/Backlog/" "$target_dir/$cr_number.md"
    sed -i '' "s/Name/$(git config user.name)/" "$target_dir/$cr_number.md"
    sed -i '' "s/YYYY-MM-DD/$(date +%Y-%m-%d)/" "$target_dir/$cr_number.md"

    # Update Implementation Plan
    echo "Updating Implementation Plan..."
    sed -i '' "s/^Version: .*/Version: $today-1/" docs/implementation/IMPLEMENTATION_PLAN.md

    # Update Working Notes
    echo "Updating Working Notes..."
    sed -i '' "s/^Version: .*/Version: $today-1/" docs/implementation/WORKING_NOTES.md

    # Stage changes
    git add "$target_dir/$cr_number.md"
    git add docs/implementation/IMPLEMENTATION_PLAN.md
    git add docs/implementation/WORKING_NOTES.md

    # Create initial commit
    git commit -m "docs(cr): create $cr_number for $title (#$issue_number)"

    echo "✅ Created:"
    echo "- Issue #$issue_number"
    echo "- Branch feature/$issue_number-${title// /-}"
    echo "- CR Document $cr_number"
    echo "- Updated Implementation Plan and Working Notes"
}

# Function to update progress
update_progress() {
    local issue_number="$1"
    local status="$2"
    local message="$3"
    local cr_number="CR-$(date +%Y.%m)-$issue_number"

    # Update GitHub issue status
    gh issue edit "$issue_number" --add-label "$status"

    # Add comment with progress
    gh issue comment "$issue_number" --body "Status: $status

    $message"

    # Move CR to appropriate directory
    move_cr "$cr_number" "$status" "$message"

    # Update Working Notes
    echo -e "\n### Progress Update ($(date +%Y-%m-%d))\n$message" >> docs/implementation/WORKING_NOTES.md

    # Commit updates
    git add "$CR_BASE_DIR"
    git add docs/implementation/WORKING_NOTES.md
    git commit -m "docs(progress): update status for #$issue_number"
}

# Function to finalize CR
finalize_cr() {
    local issue_number="$1"
    local cr_number="$2"

    # Create PR
    gh pr create --title "$(gh issue view "$issue_number" --json title --jq '.title')" \
                 --body "Closes #$issue_number" \
                 --label "ready for review"

    # Move CR to done directory
    move_cr "$cr_number" "done" "CR completed and PR created"

    # Update Working Notes with completion
    echo -e "\n### CR Completion ($(date +%Y-%m-%d))\nCompleted $cr_number (Issue #$issue_number)" >> docs/implementation/WORKING_NOTES.md

    # Commit final updates
    git add "$CR_BASE_DIR"
    git add docs/implementation/WORKING_NOTES.md
    git commit -m "docs(cr): finalize $cr_number (#$issue_number)"
}

# Main command handling
case "$1" in
    "create")
        if [ "$#" -lt 3 ]; then
            echo "Usage: $0 create 'title' 'description' 'type'"
            exit 1
        fi
        create_cr "$2" "$3" "$4"
        ;;
    "update")
        if [ "$#" -lt 4 ]; then
            echo "Usage: $0 update issue_number status 'message'"
            echo "Valid statuses: backlog, sprint-backlog, in-progress, in-review, done"
            exit 1
        fi
        update_progress "$2" "$3" "$4"
        ;;
    "finalize")
        if [ "$#" -lt 3 ]; then
            echo "Usage: $0 finalize issue_number cr_number"
            exit 1
        fi
        finalize_cr "$2" "$3"
        ;;
    *)
        echo "Usage: $0 {create|update|finalize} [args...]"
        echo "  create: Create new CR"
        echo "    $0 create 'title' 'description' 'type'"
        echo "  update: Update CR status"
        echo "    $0 update issue_number status 'message'"
        echo "    Valid statuses: backlog, sprint-backlog, in-progress, in-review, done"
        echo "  finalize: Complete CR and create PR"
        echo "    $0 finalize issue_number cr_number"
        exit 1
        ;;
esac
