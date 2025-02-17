#!/bin/bash

# Function to create a new CR
create_cr() {
    local title="$1"
    local description="$2"
    local type="$3"
    local today=$(date +%Y.%m.%d)

    # Create GitHub issue
    echo "Creating GitHub issue..."
    issue_number=$(gh issue create --title "$title" --body "$description" --label "$type" --json number --jq '.number')

    # Create branch
    echo "Creating branch..."
    git checkout -b "feature/$issue_number-${title// /-}"

    # Create CR document
    echo "Creating CR document..."
    cr_number="CR-$today-1"
    cp docs/implementation/changes/CHANGE_REQUEST_TEMPLATE.md \
       "docs/implementation/changes/$cr_number.md"

    # Update Implementation Plan
    echo "Updating Implementation Plan..."
    sed -i '' "s/^Version: .*/Version: $today-1/" docs/implementation/IMPLEMENTATION_PLAN.md

    # Update Working Notes
    echo "Updating Working Notes..."
    sed -i '' "s/^Version: .*/Version: $today-1/" docs/implementation/WORKING_NOTES.md

    # Stage changes
    git add "docs/implementation/changes/$cr_number.md"
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

    # Update GitHub issue status
    gh issue edit "$issue_number" --add-label "$status"

    # Add comment with progress
    gh issue comment "$issue_number" --body "Status: $status

    $message"

    # Update Working Notes
    echo -e "\n### Progress Update ($(date +%Y-%m-%d))\n$message" >> docs/implementation/WORKING_NOTES.md

    # Commit updates
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
