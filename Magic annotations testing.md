
# Testing Magic Annotations

## Introduction

Hello, team! We're embarking on a critical task of assessing the efficiency of our current fillable fields detection mechanism within PDFs. We need a mix of documents for this exercise, including both PDF forms and standard PDFs. Your insights and feedback are vital in this phase, so please come prepared with a few documents for testing.

## Test Procedure

Follow these steps to participate in the testing:

1.  Navigate to our testing environment by clicking [here](https://colab.research.google.com/github/andrii-harbour/magic-annotations-colab/blob/main/colab/main.ipynb).
    
2.  Execute the code by clicking the "play" button on the left side of each code block. Please wait for each to complete before moving on to the next one. ![instruction image](https://github-production-user-asset-6210df.s3.amazonaws.com/120495135/277471161-d4927f7a-4b1b-49c7-bac1-86ebd1419ce7.png)
    
3.  Access the 'magic-annotations-colab' from the folder tab in the sidebar.
![instruction image](https://github.com/andrii-harbour/magic-annotations-colab/assets/120495135/fb2090b9-8364-4913-b20d-e1246a64dbfc)
    
4.  Execute the 3rd code block, then upload your test PDF file and wait for the processing to conclude.
  ![instruction image](https://github.com/andrii-harbour/magic-annotations-colab/assets/120495135/41b2332d-a718-4635-9394-fc368bb99bdc)
    
5.  Review the results in the "output" folder; you can view each image by double-clicking on it.
	![instruction image](https://github.com/andrii-harbour/magic-annotations-colab/assets/120495135/e97dbb4b-6b7c-498e-a548-ca096265e5af)
    
### P.S. Video version [click here](https://cdn.zappy.app/3a9b0a8921a18c03cd8bb3faf199189a.mp4)

## Test Requirements

Please bring a variety of PDFs for a comprehensive test:

-   PDF forms with fillable fields.
-   Regular PDFs where `____________` indicates a fillable space.

As you test, jot down any observations regarding potential improvements or any malfunctions. Achieving 100% accuracy is challenging, but with your feedback, we aim to enhance clarity and performance as much as possible. Opt for documents that are as close to real-life use cases as possible.

## Expected Outcomes

While reviewing the results, keep the following in mind:

1.  False positives may occur. For instance, the system may incorrectly identify `__________` as a fillable field when it's actually text or a simple design element.
    
2.  The system doesn't label fields for form-based documents since form names often lack meaningful context. For regular PDFs, labels may be absent if surrounding keywords are missing or if OCR fails to recognize them.
    

Keywords the system looks for include:

 - 'date',
 -  'name',
 -  'address',
 -  'city',
 -  'state',
 -  'country',
 -  'zip',
 - 'phone',
 -  'email',
 -  'signature',
 -  'initials',
 -  'ssn',
 -  'title',
 -  'company'

## Sharing Your Findings

When you've completed the testing, please share your insights directly with me, Andrii, in the chat. Your detailed feedback is invaluable, so don't hesitate to include:

-   Your general thoughts and suggestions.
-   Specific files that presented issues.
-   Screenshots illustrating the problems encountered.

The more comprehensive and detailed your feedback, the more effectively we can work towards refining our tool.

## Good Luck!
![Good luck](https://github.com/andrii-harbour/magic-annotations-colab/assets/120495135/af7c5bb4-e133-4059-b766-e486f90ba605)
