### README

## Project Overview

This project generates a report based on a sample of 100 random items from a specified contract. The report includes various analyses and is saved as a PDF file.

## Prerequisites

- Docker
- Docker Compose

## Setup

1. **Build the Docker Image:**

   ```sh
   docker build -t gsads .
   ```

2. **Run the Docker Container:**

   ```sh
   docker run --rm -it -v $(pwd)/output:/app/output gsads
   ```

## Docker Commands

- **Build the Docker Image:**

  ```sh
  docker build -t gsads .
  ```

- **Run the Docker Container:**

  ```sh
  docker run --rm -it -v $(pwd)/output:/app/output gsads
  ```

## Project Structure

- `src/main.py`: Main script to run the report generation.
- `src/utils/report.py`: Contains the `SamplePriceComp` class for generating the report.
- `Dockerfile`: Docker configuration file.
- `requirements.txt`: Python dependencies.

## Usage

 **Run the Docker Container:**

   ```sh
   docker build -t gsads . && docker run --rm -it -v $(pwd)/output:/app/output gsads
   ```

The generated PDF report will be saved in the `output` directory.

Got it! You want to create a new branch called `GSADS` in your main web app repository (`https://github.com/cvantienen/gsa`), and this branch will track the Python scripts used in the web app (from `https://github.com/cvantienen/GSA-Data-Scripts`).

Here’s how you can go about it:

### **Step-by-Step Commands**:

#### 1. **Clone the `gsa` repository (if you haven’t already)**:
If you don’t have the `gsa` repository on your local machine, clone it:
```bash
git clone https://github.com/cvantienen/gsa.git
cd gsa
```

#### 2. **Create and Checkout the `GSADS` Branch**:
Now that you're in the `gsa` repository, create a new branch called `GSADS`:
```bash
git checkout -b GSADS
```
This command:
- Creates a new branch named `GSADS`.
- Switches your working directory to the `GSADS` branch.

#### 3. **Add the `GSA-Data-Scripts` Repository as a Remote**:
Next, you'll need to add the `GSA-Data-Scripts` repository as a remote, so you can bring in the data scripts from that repository.

To do this, add a new remote (let’s call it `datascripts`):
```bash
git remote add datascripts https://github.com/cvantienen/GSA-Data-Scripts.git
```

#### 4. **Fetch the Data Scripts**:
Now that the `GSA-Data-Scripts` repository is added as a remote, fetch its contents:
```bash
git fetch datascripts
```

#### 5. **Merge or Check Out Data from `GSA-Data-Scripts`**:
You have a couple of options here depending on whether you want to bring over the entire history or just a snapshot of the files from `GSA-Data-Scripts`.

##### **Option 1: Merging the `GSA-Data-Scripts` Content**:
If you want to merge the contents of `GSA-Data-Scripts` into the `GSADS` branch (but keep all histories separate), you can merge the content like so:
```bash
git merge datascripts/main --allow-unrelated-histories
```
- This assumes that the `GSA-Data-Scripts` repository's default branch is `main`. Adjust if it’s different.
- The `--allow-unrelated-histories` flag is necessary because these two repositories have different histories.

##### **Option 2: Checking Out Files from `GSA-Data-Scripts`**:
If you want to **bring over the files** (without merging the entire history), you can check out just the files from the `GSA-Data-Scripts` repository into the `GSADS` branch:
```bash
git checkout datascripts/main -- path/to/your/data/scripts
```
This will copy the files from the `GSA-Data-Scripts` repository into your `GSADS` branch without bringing over the full commit history.

#### 6. **Stage and Commit the Data Scripts (if needed)**:
Once you’ve merged or checked out the data scripts, you might need to stage and commit the changes if any new files were added to the branch:
```bash
git add .
git commit -m "Add data scripts from GSA-Data-Scripts repo"
```

#### 7. **Push the `GSADS` Branch to GitHub**:
Now, push the new `GSADS` branch to your `gsa` repository on GitHub:
```bash
git push origin GSADS
```

This will push the `GSADS` branch to your GitHub repository.

---

### **Summary of Commands**:
Here’s the full sequence of commands to achieve what you're asking for:

```bash
# Step 1: Clone the gsa repo (if you haven't already)
git clone https://github.com/cvantienen/gsa.git
cd gsa

# Step 2: Create and checkout the GSADS branch
git checkout -b GSADS

# Step 3: Add the GSA-Data-Scripts repo as a remote
git remote add datascripts https://github.com/cvantienen/GSA-Data-Scripts.git

# Step 4: Fetch the content from the data scripts repo
git fetch datascripts

# Step 5: Merge or check out the data scripts (depending on your choice)
# Option 1: Merging
git merge datascripts/main --allow-unrelated-histories

# Option 2: Checking out files (if you just want to copy them over)
git checkout datascripts/main -- path/to/your/data/scripts

# Step 6: Stage and commit the changes
git add .
git commit -m "Add data scripts from GSA-Data-Scripts repo"

# Step 7: Push the GSADS branch to GitHub
git push origin GSADS
```

---

With this, you will have successfully created a `GSADS` branch in your main `gsa` repository, added the data scripts from the `GSA-Data-Scripts` repository, and pushed the `GSADS` branch to GitHub.

Let me know if any part needs more clarification!