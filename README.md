# Lean Autograder
A semi-automatic grading script for proofs written in the [Lean theorem prover.](https://leanprover.github.io/)

Grades a folder of `.lean` files based on a template `.lean` file.

This autograder requires that [Lean is installed and in the PATH.](https://leanprover-community.github.io/get_started.html)

## Usage

```
python3 autograder.py directory/containing/submissions homework/template.lean
```
The template file should consist of various unsolved proofs headed with `example`, with the body of the proof consisting only of `sorry`, as follows:
```lean
variable A : Prop

example : A → A :=
  sorry
  
example : A ∨ ¬A :=
  sorry
  
example : A ∧ ¬A := -- OPTIONAL
  sorry
```
An `example` line suffixed with `-- OPTIONAL` is not graded.

In many cases, this can be used as the template file that is given to the students, who are then assigned to replace each `sorry` with a correct proof.

Each file is given a score on a 100-point scale, wherein all proofs are of the same point value and there is no partial credit for missing or incorrect proofs: thus, human review is needed for assignment of partial credit / forgiveness of minor syntax errors. For this, files that are missing any theorems, or contain errors, are moved to a subdirectory named "For Review", while files with no errors are moved to a subdirectory named "Perfect".

This autograder also functions on files inside a `leanproject`.

## Roadmap
- [ ] More options for file sorting
- [ ] Per-question point values
- [ ] Mark proofs as incorrect if they contain keywords marked in the template as "banned"
- [ ] Processing speed: use single Lean process for entire batch of submissions
