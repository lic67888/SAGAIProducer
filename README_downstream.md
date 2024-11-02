# python-template
REPLACE_ME_DESCRIPTION

* [python-template](https://github.com/lite-dsa/python-template)
* [Poetry](https://python-poetry.org/)
    * For dependency management, packaging, and publishing
* [Ruff](https://github.com/astral-sh/ruff)
    * For linting/formatting (it's FAST)
* GitHub Actions
    * For CI/CD
* [Pytest](https://docs.pytest.org/en/8.2.x/)
    * For testing
* [pre-commit](https://pre-commit.com/)
    * For pre-commit hooks
* [PyInvoke](http://www.pyinvoke.org/)
    * For task running, because I hate `make`


## To get started
1. Clone the repo
2. If poetry isn't installed, [you need to install it](https://python-poetry.org/docs/#installation).  
3. terminal `cd` into the project
3. run `poetry install`
3. Run `poetry run inv setup`
    

The setup will  
* Setup the poetry environment (or use the existing one you're activated to)
* Install the dependencies
* Setup the pre-commit hooks 

## Contributing
If you have any suggestions, please open an issue.  If you'd like to contribute, please open a pull request.  I'm always looking for ways to improve this template. I'm open to suggestions, but I'm also very opinionated.  I'm trying to keep it as simple as possible while remaining good enough for production code.

## Updating from template
If you want to update your project from the template, or add the template to an existing project. 
There's a handy inv task. Just run `inv setup.update-from-template`.

or you can do it manually with the following commands

```bash
git remote add template https://github.com/lite-dsa/python-template.git
git fetch template
git merge template/main --allow-unrelated-histories
```
