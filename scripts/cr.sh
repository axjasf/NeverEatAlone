#!/bin/bash

# Constants for directory structure
CR_BASE_DIR="docs/features"
CR_BACKLOG_DIR="$CR_BASE_DIR/1-backlog"
CR_SPRINT_DIR="$CR_BASE_DIR/2-sprint-backlog"
CR_PROGRESS_DIR="$CR_BASE_DIR/3-in-progress"
CR_REVIEW_DIR="$CR_BASE_DIR/4-in-review"
CR_DONE_DIR="$CR_BASE_DIR/5-done"
CR_TEMPLATE="$CR_BASE_DIR/CHANGE_REQUEST_TEMPLATE.md"

# Function to ensure directories exist
ensure_directories() {
    mkdir -p "$CR_BACKLOG_DIR"
    mkdir -p "$CR_SPRINT_DIR"
    mkdir -p "$CR_PROGRESS_DIR"
    mkdir -p "$CR_REVIEW_DIR"
    mkdir -p "$CR_DONE_DIR"
}

# Function to get target directory based on status
get_target_dir() {
    local status="$1"
    case "$status" in
        "backlog") echo "$CR_BACKLOG_DIR" ;;
        "sprint-backlog") echo "$CR_SPRINT_DIR" ;;
        "in-progress") echo "$CR_PROGRESS_DIR" ;;
        "in-review") echo "$CR_REVIEW_DIR" ;;
        "done")
            local year_month=$(date +"%Y/%m")
            local target="$CR_DONE_DIR/$year_month"
            mkdir -p "$target"
            echo "$target"
            ;;
        *) echo "$CR_BACKLOG_DIR" ;;  # Default to backlog
    esac
}

# Function to create a new CR
create_cr() {
    local title="$1"
    local description="$2"
    local type="$3"
    local today=$(date +%Y.%m.%d)

    ensure_directories

    # Verify template exists
    if [ ! -f "$CR_TEMPLATE" ]; then
        echo "Error: Template file $CR_TEMPLATE not found"
        exit 1
    fi

    # Create GitHub issue
    echo "Creating GitHub issue..."
    issue_number=$(gh issue create --title "$title" --body "$description" --label "$type" --json number --jq '.number')

    # Create branch
    echo "Creating branch..."
    git checkout -b "feature/$issue_number-${title// /-}"

    # Get feature number from user
    read -p "Enter feature number (e.g., 1 for data-model): " feature_num
    feature_dir=$(find "$CR_BASE_DIR" -type d -name "${feature_num}-*" | head -n 1)

    if [ -z "$feature_dir" ]; then
        echo "❌ Feature directory not found for number $feature_num"
        exit 1
    fi

    # Create CR in feature directory
    mkdir -p "$feature_dir/crs"
    cr_path="$feature_dir/crs/CR-$today-$issue_number.md"
    cp docs/development/guides/cr/CHANGE_REQUEST_TEMPLATE.md "$cr_path"

    # Update feature OVERVIEW.md
    echo "- [ ] CR-$today-$issue_number: $title" >> "$feature_dir/OVERVIEW.md"

    # Update Implementation Plan
    echo "Updating Implementation Plan..."
    sed -i '' "s/^Version: .*/Version: $today-1/" docs/implementation/IMPLEMENTATION_PLAN.md

    # Update Working Notes
    echo "Updating Working Notes..."
    sed -i '' "s/^Version: .*/Version: $today-1/" docs/implementation/WORKING_NOTES.md

    # Stage changes
    git add "$feature_dir/crs/CR-$today-$issue_number.md"
    git add docs/implementation/IMPLEMENTATION_PLAN.md
    git add docs/implementation/WORKING_NOTES.md

    # Create initial commit
    git commit -m "docs(cr): create CR-$today-$issue_number for $title (#$issue_number)"

    echo "✅ Created:"
    echo "- Issue #$issue_number"
    echo "- Branch feature/$issue_number-${title// /-}"
    echo "- CR Document CR-$today-$issue_number in feature $feature_num"
    echo "- Updated Implementation Plan and Working Notes"
}

# Function to update progress
update_progress() {
    local issue_number="$1"
    local status="$2"
    local message="$3"
    local cr_file

    # Find the CR file
    cr_file=$(find "$CR_BASE_DIR" -type f -name "CR-*.md" -exec grep -l "Issue Number: #$issue_number" {} \;)

    if [ -z "$cr_file" ]; then
        echo "Error: Could not find CR file for issue #$issue_number"
        exit 1
    fi

    # Get target directory
    target_dir=$(get_target_dir "$status")

    # Move CR file to new status directory
    mv "$cr_file" "$target_dir/$(basename "$cr_file")"

    # Update GitHub issue status
    gh issue edit "$issue_number" --add-label "$status"

    # Add comment with progress
    gh issue comment "$issue_number" --body "Status: $status

    $message"

    # Update Working Notes
    echo -e "\n### Progress Update ($(date +%Y-%m-%d))\n$message" >> docs/implementation/WORKING_NOTES.md

    # Commit updates
    git add "$target_dir/$(basename "$cr_file")"
    git add docs/implementation/WORKING_NOTES.md
    git commit -m "docs(progress): update status for #$issue_number to $status"
}

# Function to finalize CR
finalize_cr() {
    local issue_number="$1"
    local cr_number="$2"

    # Create PR
    gh pr create --title "$(gh issue view "$issue_number" --json title --jq '.title')" \
                 --body "Closes #$issue_number" \
                 --label "ready for review"

    # Update Working Notes with completion
    echo -e "\n### CR Completion ($(date +%Y-%m-%d))\nCompleted $cr_number (Issue #$issue_number)" >> docs/implementation/WORKING_NOTES.md

    # Commit final updates
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
        exit 1
        ;;
esac
