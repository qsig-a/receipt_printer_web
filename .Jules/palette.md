[Output truncated for brevity]

lways disable action buttons when the related dataset is empty, and provide clear explanations via tooltips (`title` attribute) and `aria-disabled="true"` to inform users why the action is unavailable.

## 2026-03-10 - Scrollable Table Accessibility
**Learning:** Tables that scroll vertically hide their column headers, confusing users. Furthermore, if a table container is scrollable, keyboard-only users cannot scroll it without `tabindex="0"`.
**Action:** Always make table headers sticky (`position: sticky; top: 0; z-index: 10;`) and wrap scrollable tables in a container with `tabindex="0"`, `role="region"`, and a descriptive `aria-label` to ensure they are fully navigable by keyboard and screen reader users. Also provide a custom `:focus-visible` outline for the container to highlight it when focused.

## 2026-03-11 - Explicit Error Associations
**Learning:** Relying solely on visual cues (like a red border) and `aria-invalid="true"` is insufficient for screen reader users to understand *why* an input is invalid if the error message is disconnected from the input in the DOM.
**Action:** Always use `aria-errormessage` on the invalid input, pointing to the `id` of the element containing the explicit error message, to provide clear, actionable feedback to screen reader users. Ensure this attribute is cleared simultaneously with `aria-invalid` when the user begins typing.

## 2026-03-11 - Accessible Copy Feedback
**Learning:** Changing an emoji in a copy-to-clipboard button (e.g., from 📋 to ✅) provides excellent visual feedback for sighted users, but offers absolutely no context to screen reader users about the outcome of the action.
**Action:** When updating a button's visual state to indicate success, concurrently update its `aria-label` and `title` attributes (e.g., to "Copied!") for the duration of the feedback state, ensuring equitable access to status updates.

## 2026-03-11 - Hiding Decorative Emojis
**Learning:** Using inline emojis for visual flair in headings or empty states can create jarring experiences for screen reader users, as the emojis are often read out with long, literal descriptions (e.g., "Remote Print fax machine").
**Action:** Wrap purely decorative emojis in a `<span aria-hidden="true">` to hide them from assistive technologies while preserving the visual design for sighted users.

## 2026-03-12 - Auth Failure Dead End Escape Hatch
**Learning:** Returning a raw "Unauthorized" text response or trapping unauthenticated users on a login screen without a clear exit path creates a dead end, forcing them to use the browser back button, which is poor UX.
**Action:** Always provide an "escape hatch" (like a "Back to Portal" link) on protected views or login screens so unauthenticated users can easily return to the main application flow.

## 2026-03-13 - State Communication for Toggle Buttons
**Learning:** Toggle buttons (like password visibility toggles) without explicit state attributes leave screen reader users unsure of the current state or the outcome of their action.
**Action:** Always use the `aria-pressed` attribute (toggling between `"true"` and `"false"`) on semantic `<button>` elements that act as toggles, and use `aria-controls` to explicitly link them to the element they modify, ensuring clear state communication for assistive technologies.

## 2026-03-13 - Toggle Button Anti-Pattern
**Learning:** Changing both the `aria-label` (e.g., from "Show password" to "Hide password") and the `aria-pressed` state simultaneously on a toggle button is a known W3C ARIA anti-pattern. Doing both results in confusing screen reader announcements like "Hide password, toggle button, pressed".
**Action:** For a true toggle button, either keep the `aria-label` static (e.g., "Show password" or "Toggle password visibility") while toggling `aria-pressed` between true/false, OR change the `aria-label` dynamically without using `aria-pressed`. Do not combine both approaches.

## 2026-03-14 - Data Table Scannability and Semantics
**Learning:** Wide data tables without visual aids (like hover states) cause users to lose their place when tracking across columns. Furthermore, generic markup (`<span>` for dates, `<th>` without scope) limits the usefulness of the data for screen reader users and automated parsing.
**Action:** Always include a subtle `.history-table tbody tr:hover` state for multi-column data tables to improve horizontal tracking. Additionally, ensure table headers explicitly declare `scope="col"`, use semantic `<time datetime="...">` tags for temporal data, and define explicit `type="button"` on in-row utility buttons to prevent accidental form submissions.

## 2026-03-15 - Accessible Loading States for Form Submissions
**Learning:** Disabling a submit button and changing its text (e.g., "Sending... ⏳") provides great visual feedback, but screen reader users may not be aware of the state change if the element simply becomes disabled.
**Action:** Always add `aria-busy="true"` to submit buttons when a form is actively processing. This explicitly informs assistive technologies that the element is in a loading or busy state.
## 2026-03-17 - Empty States with Call-to-Action
**Learning:** Basic empty states (like "No print history found") leave users at a dead end, especially in a new application where they might not know how to generate data.
**Action:** Always enhance empty states with a helpful call-to-action or guidance (e.g., "Send a message from the portal to see it here.") to direct users towards the desired next step.
