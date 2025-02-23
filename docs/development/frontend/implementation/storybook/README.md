# Storybook Implementation Guide

## Overview

This document outlines the Storybook setup and implementation guidelines for the Contact Management System's frontend components. It provides concrete examples of component implementation following the UX specifications and BRD requirements.

## Setup

### Configuration
```typescript
// .storybook/main.ts
import type { StorybookConfig } from '@storybook/react-vite';

const config: StorybookConfig = {
  stories: ['../src/**/*.mdx', '../src/**/*.stories.@(js|jsx|mjs|ts|tsx)'],
  addons: [
    '@storybook/addon-links',
    '@storybook/addon-essentials',
    '@storybook/addon-interactions',
    '@storybook/addon-a11y',
  ],
  framework: '@storybook/react-vite',
  docs: { autodocs: 'tag' },
};

export default config;
```

## Component Stories

### 1. Contact View Component
Implements FR4.2.1 (Show only filled fields in view mode):

```typescript
// src/stories/components/ContactView.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { ContactView } from '../../components/ContactView';

const meta = {
  title: 'Contact Management/ContactView',
  component: ContactView,
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof ContactView>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    contact: {
      id: '1',
      name: 'John Smith',
      first_name: 'John',
      sub_information: {
        personal: {
          spouse: 'Jane Smith',
          languages: ['English', 'German']
        },
        professional: {
          company: 'TechCorp',
          role: 'CTO'
        }
      },
      hashtags: ['#tech', '#monthly-call'],
      notes: [
        {
          id: 1,
          text: 'Met for coffee, discussed AI initiatives',
          statements: [
            'Interested in expanding AI team',
            'Planning move to Amsterdam'
          ]
        }
      ]
    },
    mode: 'view'
  }
};

export const EditMode: Story = {
  args: {
    ...Default.args,
    mode: 'edit'
  }
};
```

### 2. Notes System Component
Implements FR2.1 (Note Management) and FR3.1 (Voice Processing):

```typescript
// src/stories/components/NotesSystem.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { NotesSystem } from '../../components/NotesSystem';

const meta = {
  title: 'Contact Management/NotesSystem',
  component: NotesSystem,
  parameters: {
    layout: 'fullscreen',
  },
} satisfies Meta<typeof NotesSystem>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Recording: Story = {
  args: {
    isRecording: true,
    processingState: 'recording'
  }
};

export const Processing: Story = {
  args: {
    isRecording: false,
    processingState: 'processing',
    note: {
      text: "Had a great meeting with John...",
      statements: [
        "Moving to Amsterdam next month",
        "Taking new role as CTO"
      ]
    }
  }
};
```

### 3. Ring Management Component
Implements FR1.3 (Ring Organization) and FR4.1.3 (Ring Management UI):

```typescript
// src/stories/components/RingManagement.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { RingManagement } from '../../components/RingManagement';

const meta = {
  title: 'Contact Management/RingManagement',
  component: RingManagement,
} satisfies Meta<typeof RingManagement>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    rings: [
      {
        id: 1,
        name: "Monthly Check-ins",
        frequency: 30,
        contacts: 15,
        nextDue: "2024-02-15"
      }
    ]
  }
};
```

### 4. Template Manager Component
Implements FR1.2 (JSON Information) and FR4.1.2 (Template Management UI):

```typescript
// src/stories/components/TemplateManager.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { TemplateManager } from '../../components/TemplateManager';

const meta = {
  title: 'Contact Management/TemplateManager',
  component: TemplateManager,
} satisfies Meta<typeof TemplateManager>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    template: {
      personal: {
        spouse: { display_name: 'Spouse', type: 'string' },
        languages: { display_name: 'Languages', type: 'array' }
      },
      professional: {
        company: { display_name: 'Company', type: 'string' },
        role: { display_name: 'Role', type: 'string' }
      }
    }
  }
};
```

## Testing with Storybook

### 1. Interaction Tests
```typescript
// Example interaction test for ContactView
import { expect } from '@storybook/jest';
import { within, userEvent } from '@storybook/testing-library';

export const EditModeInteraction: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const editButton = await canvas.findByRole('button', { name: /edit/i });
    await userEvent.click(editButton);

    // Verify edit mode is active
    const nameInput = await canvas.findByRole('textbox', { name: /name/i });
    await expect(nameInput).toBeInTheDocument();
  }
};
```

### 2. Accessibility Tests
```typescript
// Example a11y configuration
export const Default: Story = {
  parameters: {
    a11y: {
      config: {
        rules: [
          {
            id: 'color-contrast',
            enabled: true
          }
        ]
      }
    }
  }
};
```

## Documentation Standards

### 1. Component Documentation
```typescript
/**
 * ContactView component
 *
 * Displays contact information in either view or edit mode.
 * Implements FR4.2.1 for showing only filled fields in view mode.
 *
 * @component
 * @example
 * ```tsx
 * <ContactView
 *   contact={contact}
 *   mode="view"
 *   onSave={handleSave}
 * />
 * ```
 */
```

### 2. Story Documentation
```typescript
// Example story documentation
Default.parameters = {
  docs: {
    description: {
      story: 'Default view mode showing only filled fields as per FR4.2.1'
    }
  }
};
```

## References

1. [UX Specifications](../ux-specifications.md)
2. [Frontend Implementation Guide](../README.md)
3. [Functional Requirements](../../../brd/modules/contact_management/requirements/functional.md)
4. [Technical Architecture](../../../brd/modules/contact_management/technical/architecture.md)
