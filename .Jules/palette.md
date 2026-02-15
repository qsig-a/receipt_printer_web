## 2024-05-22 - Accessibility in Embedded Templates
**Learning:** This Flask application embeds HTML templates directly in Python strings, which led to missing standard accessibility features like `<label>` elements and viewport meta tags.
**Action:** When working with embedded templates, explicitly check for and add `<label>` elements and responsiveness meta tags to ensure basic accessibility and mobile usability.

## 2025-02-23 - Status Message Accessibility
**Learning:** The application uses a generic `.status-box` div for feedback, which is not announced by screen readers on page reload.
**Action:** Always add `role="alert"` to feedback containers in server-rendered templates to ensure screen reader users are immediately aware of the form submission outcome.

## 2025-05-23 - Visible Constraints for Better UX
**Learning:** The application enforces a `CHARACTER_LIMIT` on the backend but provided no visual indication on the frontend, leading to a frustrating "error-after-submit" experience.
**Action:** When backend constraints exist, surface them in the UI (e.g., character counters, `maxlength` attributes) to prevent errors before they happen.

## 2025-05-24 - Persist User Input on Error
**Learning:** Users lose their typed message if the submission fails (e.g., wrong password), causing significant frustration.
**Action:** Always re-populate form fields with the submitted data when rendering an error state, so users can correct the issue without retyping.
