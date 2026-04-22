# HR Operations Automation using n8n

This project automates the candidate communication workflow by integrating Google Sheets,n8n, and email services. It dynamically sends personalized emails to candidates based on their application status using templates stored in a Word (.docx) document.

## Project Overview
The workflow monitors a candidate tracker (Google Sheet) and triggers automated email notifications at different stages of the hiring process.

Unlike hardcoded solutions, this system:
* Fetches email templates from a `.docx` file
* Replaces placeholders dynamically with candidate data
* Sends personalized emails automatically

## Key Features
* Google Sheets as the central candidate tracker
* Dynamic email templates from `.docx` file
* Status-based workflow automation
* Personalized email notifications
* Prevents duplicate emails using `email_sent` column
* Real-time or scheduled execution

## Workflow Architecture
Google Sheets (Candidate Data)
        ↓
Check New Row / Status Change
        ↓
Fetch Template from .docx File
        ↓
Replace Placeholders ({{Name}}, {{Task_Link}}, etc.)
        ↓
Send Email to Candidate
        ↓
Update "Email_sent" Column


## Email Template Handling
Email content is stored in a Word document (`HR_Email_Templates.docx`).

The workflow:
1. Reads the `.docx` file
2. Extracts template content
3. Replaces placeholders dynamically

### Supported Placeholders:
* `{{Name}}` → Candidate Name
* `{{Task_Link}}` → Task URL
* `{{Skills}}` → Candidate Skills
* `{{Education}}` → Candidate Education

## Workflow Stages

### Stage 1: New Entry
* Trigger: New row added OR Status is `New` / blank
* Action: Send "Thank You / Task Assignment" email

### Stage 2: Shortlisted
* Trigger: Status updated to `Shortlisted`
* Action: Send "Shortlisted / Next Steps" email

### Stage 3: Completed
* Trigger: Status updated to `Completed`
* Action: Send "Process Completed" email

## Tools & Technologies
*  n8n– Workflow automation
*  Google Sheets – Candidate data management
*  Google Drive – DOCX storage
*  Gmail– Email delivery

## How to Use
1. Create a Google Sheet with columns:

   * Name
   * Email
   * Task Link
   * Status
   * email_sent

2. Upload `HR_Email_Templates.docx`(Google Drive).

3. Import the `workflow.json` into n8n

4. Configure credentials:

   * Google Sheets API
   * Google Drive (if used)
   * Email (SMTP / Gmail)

5. Run or activate the workflow

## Project Structure
hr-automation/
├── workflow.json
├── HR_Email_Templates.docx
└── screenshots/
    ├── google-sheet.png
    ├── workflow.png
    ├── docx.png
    └── email-new.png

## Important Notes

* Ensure status values match exactly:
  * New / blank
  * Shortlisted`
  * Completed`
* email_sent column is used to prevent duplicate emails
* Do not share API keys or credentials
* Test workflow before production use

## Future Enhancements
* Auto-trigger on Google Sheet updates
* Resume parsing automation
* AI-based candidate filtering
* HR analytics dashboard

## Use Cases
* HR teams
* Recruiters
* Startups
* Small businesses

## Author
 Pavitra Maradi
 [pavitramaradi109@gmail.com](mailto:pavitramaradi109@gmail.com)
 https://www.linkedin.com/in/pavitra-maradi
