# stepik-cli
A command line interface for [the Stepik API](https://stepik.org/api/docs)

## Commands
```
$ stepik --help
Usage: stepik [OPTIONS] COMMAND [ARGS]...

  The (unofficial) Stepik CLI for students

  A command line tool for submitting solutions to stepik.org

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  auth     Authenticate using your OAuth2 credentials.
  content  View the content of a course, section, or lesson by its ID.
  course   Switch to the course that has the provided course ID.
  courses  Display a list of your enrolled courses and their course IDs.
  current  Display the URL and step ID of the current step.
  dataset  Attempt a dataset challenge.
  lang     Lists the available programming languages for the current step.
  next     Navigate to the next step in a course.
  prev     Navigate to the previous step in a course.
  step     Navigate the current position to the step at the provided URL.
  submit   Submit a solution to stepik.
  text     Display the contents of the current step.
  type     Filter for steps with this step type.
```

## Installation
Via `pip`:
```
pip install stepik-cli
```

## Setup
1. Create an account on [stepik.org](https://stepik.org/)
2. Enroll in courses
3. [Create a new OAuth2 application](https://stepik.org/oauth2/applications/register/) with the following information
    - **Name**: _stepikcli_
    - **Client type**: _confidential_
    - **Authorization Grant Type**: _client-credentials_
    - **Redirect uris**: N/A (ie leave this field blank)

    Save the client ID and client secret for later use (see #4 below)
4. Authenticate yourself with the CLI
    ```
    stepik auth
    ```
    Enter the client ID and client secret from #3 above
5. View a list of the course IDs for each of your courses. Pick one of them to submit your solutions to.
    ```
    stepik courses
    ```
6. Set the current course. You can always change this later.
    ```
    stepik course <course-id>
    ```
    For this command, replace `<course-id>` with the course ID you chose in #5.

## Navigation
Just like the Stepik website, you can navigate between steps within your chosen course.

Once you've navigated to a step, the CLI will remember your position in the course.

### Setting your current step
To start, you must jump to a step within the course:
```
stepik step <url>
```
You should replace `<url>` with the link to the step (ex: `https://stepik.org/lesson/9172/step/2`)

You can check your current position in the course at any time.
```
stepik current
```

You can also view the content of the current step.
```
stepik text
```

### Navigating to the next or previous step
Once you've navigated to a step, you can move back or forth within the course.
```
stepik next
# or
stepik prev
```

Each step has a _type_ that describes its content. For example, steps containing dataset challenges will have the _dataset_ type. When navigating between steps, you can instruct the Stepik CLI to filter for a specific step type. To set the step type, use the `type` command.
```
stepik type dataset
```

### Viewing the table of contents of a course
Each course is made up of sections. Each section is made up of lessons. And each lesson is made up of steps.

You can view the content at any level of this hierarchy.
```
stepik content course <course-id>
stepik content section <section-id>
stepik content lesson <lesson-id>
```

## Submissions
To submit a solution to a problem, you must first set the current step.
```
stepik step <url>
```
You should replace `<url>` with the link to the step (ex: `https://stepik.org/lesson/9172/step/2`)

### Attempting a dataset challenge
To submit to a dataset challenge, you should first download a dataset from this step.
```
stepik dataset <dataset-path>
```
You should replace `<dataset-path>` with the path to a file in which you'd like to store the dataset.

### Submitting a solution
To submit to a dataset challenge, you must first write your solution to a file.
```
stepik submit <solution-path>
```
You should replace `<solution-path>` with the path to the file that contains your solution.

### Attempting a code or text challenge
To submit to a code or text challenge, you should use the `-l` optional argument to specify the programming language of your submission.
```
stepik submit -l python3 solution.py   # to submit to a code challenge
stepik submit -l text solution.txt     # to submit to a text challenge
```
You can view a list of the available programming languages.
```
stepik lang
```

### Example: Submitting to a dataset challenge
As an example, let's consider [this dataset challenge](https://stepik.org/lesson/9172/step/2). To follow along, you must first register for [this course on the Stepik website](https://stepik.org/course/1/syllabus) and complete [the setup process](#Setup), including the authentication step.
```
# switch to this course
stepik course 1
# set the step
stepik step https://stepik.org/lesson/9172/step/2
# view the problem statement
stepik text
# download the dataset
stepik dataset dataset.txt
# solve the problem and create a solution file
cat dataset.txt | tr ' ' '+' | bc > solution.txt
# submit the solution
stepik submit solution.txt
```

## Help
Every command in the CLI has a `--help` argument with more detailed descriptions.

## Bugs, Contributions, and Suggestions
I welcome reports of bugs and/or suggestions for improvements to this software within Github's issue tab.

However, I have limited capacity to maintain the code in this repository. If you would like to see a bug fixed, consider forking this repository and creating a pull request. I will gladly consider all submitted pull requests!

I am not a member of the Stepik team. Nor am I in any way affiliated with them. I make no guarantee that this software will not eventually break, especially if Stepik ever changes their API.
