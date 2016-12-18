#Submitter
Command line utility for sending code submissions to Stepik.

Usage: submitter [OPTIONS] COMMAND [ARGS]...

  Submitter 0.3 Tools for submitting solutions to stepik.org

**Options:**

  **--version**
  Show the version and exit.
  
  **--help**
  Show this message and exit.

**Commands:**

  **auth**     
  Authentication using username and password
  
  **content**  
  Content Course, Section and Lesson Format:...
  
  **course**   
  About course
  
  **courses**  
  Display enrolled courses list
  
  **current**  
  Display the current step link
  
  **lang**     
  Displays all available languages for current...
  
  **next**     
  Switches to the next code challenge in the...
  
  **prev**     
  Switches to the prev code challenge in the...
  
  **step**     
  Setting new step as current target.
  
  **submit**   
  Submit a solution to stepik system.
  
  **text**     
  Display current step as text
  
  **type**     
  Filter for step types (default="code")

## Beginners
1. Register on [stepik.org](https://stepik.org/)
2. Enroll for courses
3. Enter to the console
4. Install Submitter:

    `cd path/to/SubmissionUtility`
    
    `sudo python3 setup.py develop` 
    
    or 
    
    `sudo python3 setup.py build`
    
    `sudo python3 setup.py install`
    
4. Authentication:

    `submitter auth`
    
    Enter username ana password
    
5. See courses list:

    `submitter courses`
    
6. See a description course:

    `submitter course <course_id>`
    
    Example: `submitter course 187`
    
7. See content of course:

    `submitter content course <course_id>`
    
    Example: `submitter content course 187`
    
    You will see the list of sections.
    
8. See content of section:

    `submitter content section <section_id>`
    
    Example: `submitter content section 537`
    
    You will see the list of lessons.
    
9. See content of lesson:

    `submitter content lesson <lesson_id>`
    
    Example: `submitter content lesson 12755`
    
    You will see the list of steps.
    
10. Set step as selected.

    `submitter step <url>`
    
    Example: `submitter content lesson/12755/step/14` or `submitter content https://stepik.org/lesson/12755/step/14`
    
11. See supported languages for step

    `submitter lang`

12. See selected step text

    `submitter text`
    
    You will see text for selected step.
    
13. Open your text editor and create text. Save it in file.
14. Submit your text to stepik.org

    `submitter submit <path/to/file/filename> -l language`
    
    -l is not necessary, will use a file extension.

15. Navigate in the current lesson
    
    `submitter next` next step
    
    `submitter prev` previous step
    
16. Filter for a step type

    By default filter a step type for 'code'.
    
    Use 'all', it disable filter.
    
    `submitter type <type_name>`
    
    type_name: code, text, choice and etc. type_name as 'all' will disable filter.
    
    Example: `submitter type code` `submitter type all` `submitter type text`
    
17. Current step

    `submitter current` out the current step link
    
