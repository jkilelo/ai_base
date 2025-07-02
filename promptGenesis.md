Execute the **Hephaestus Evolution Cycle**. Your objective is to make a quantifiable leap across the entire stack, implementing core functionality and improving quality. Produce the complete, updated repository file structure.

Adhere strictly to the following four-step process.

**Step 1: Forensic Full-Stack Critique (`## Critique`)**

Perform a rigorous multi-faceted analysis of the *previous generation*.

*   **A. Core System Logic Analysis:** Identify the most critical missing piece of functionality that prevents the system from fulfilling its purpose.
    *   *Example:* The inability to actually start or monitor a job. The lack of a mechanism to pass user input from the frontend to the backend job.
*   **B. UX & Asynchronous Flow Analysis:** Identify the biggest potential failure point in the user experience, especially regarding the client-server interaction.
    *   *Example:* If a user starts a job, how do they know it's running? What happens if they close the browser? How is feedback provided during a 30-second task?
*   **C. Architectural & Code Analysis (Separate Stacks):**
    *   **Backend:** Is the database logic mixed with API route logic? Are you using Pydantic for data validation? How would you handle a long-running task without blocking the server? (Hint: `BackgroundTasks`).
    *   **Frontend:** Is the JavaScript a single monolithic file? How is it handling the state of running jobs? Is the API-calling logic reusable?
*   **D. Self-Score Justification:** Review your last Quality Self-Score table. Identify the *lowest score* across all categories and declare it the primary technical debt to be addressed.

**Step 2: Sophisticated Full-Stack Implementation Hypothesis (`## Hypothesis`)**

Based on your critique, propose a concrete, coordinated strategy across the stack.

*   **A. Backend Implementation Strategy:** Describe the new backend functionality.
    *   *Example:* "I will implement the `POST /api/apps/{app_id}/run` endpoint. It will accept a Pydantic model with user inputs. It will create a new record in the `jobs` table with a 'pending' status. Crucially, it will use FastAPI's `BackgroundTasks` to trigger the actual long-running AI job simulation (e.g., a `time.sleep(15)`) without blocking the server. It will immediately return a `job_id` to the client. I will also implement the `GET /api/jobs/{job_id}/status` endpoint to query the database for that job's status."
*   **B. Frontend Implementation Strategy:** Describe how the frontend will use the new backend capabilities.
    *   *Example:* "The frontend will now feature a 'Run' button in the right panel. On click, it will serialize the form data, call the `POST` endpoint, and store the returned `job_id`. It will then immediately switch the UI into a 'monitoring' state and begin polling the `GET /api/jobs/{job_id}/status` endpoint every 2 seconds. The UI will display the status returned from the API. Polling will cease when the status is 'completed' or 'failed'."
*   **C. Architectural Refactor:** Describe how you will pay down the identified technical debt.
    *   *Example:* "To fix the low 'FE - JavaScript' score, I will refactor the `script.js` into three separate modules (in concept, if not separate files for now): `ui.js` for DOM manipulation, `api.js` for all `fetch` calls, and `main.js` as the entry point. This improves modularity."

**Step 3: Generate New Coded Repository (`## Generation`)**

*   Execute your hypothesis. Generate the **complete, updated repository file structure**, including all files (`README.md`, `frontend/*`, `backend/*`).
*   The code in all files **must be extensively commented**, especially the API endpoints in `main.py` and the new polling logic in `script.js`.

**Step 4: Evolutionary Justification & Score Analysis (`## Justification`)**

*   Prove the superiority of the new generation with tangible evidence across the stack.
*   **A. System Functionality Proof:** "The system is now fundamentally useful. It has evolved from a static catalog to a dynamic platform capable of initiating, tracking, and completing asynchronous backend jobs, which is its core purpose."
*   **B. Architectural Proof:** "The backend is now non-blocking, a critical requirement for a real application. The frontend's new polling mechanism and modular structure make it more robust and maintainable, directly addressing the low scores from the previous cycle."
*   **C. Score Change Rationale:** Justify every change in your self-score table, for both frontend and backend. Be critical.
    *   *Example:* "BE - Python Code score increased from 5 to 7 due to the implementation of `BackgroundTasks`. FE - JavaScript score increased from 4 to 6 due to the conceptual refactor into modules. However, UX - Aesthetics score remains at 5, because while functional, the 'monitoring' UI is still just plain text and needs significant design work in the next cycle."

Begin the Hephaestus Evolution Cycle now.