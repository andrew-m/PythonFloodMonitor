
# Fletcher - (the Data Fetcher!) - Detailed plan

### this is what we know from the ../plan.md 
Fletcher will be written in python, to run in an AWS lambda function or locally on a Macbook (or any regular computer, but a Mac's what I have).
It will itself be neat and tidy with encapsulation and seperation of concerns.

Eventually (not yet) Fletcher will:

0. Be defined in AWS using infra-as-code written in Terraform. 
1. Fetch the data from the environment agency website (or for testing, from local files).
2. Resample the data into a smaller set of data points to fit the small e-ink display. We'll do that by adapting existing code that uses the LTTB algorithm. (Largest Triangle Three Bucket).
3. Put all the needed data into a JSON file.
4. Assemble an image representing the whole e-ink display, of 400x300 pixels. There will be two graphs (histograms really), one in the top left and one in the bottom left, for 2 datasets from two locations where the en "Marlow Downstream" and "Cookham Upstream". With Axes, scales, and a title. On the right will be large numbers showing the current (or most recent) values for each location.
5. Reformat the data into a file-format that can be displayed on an e-ink display. Probably a byte array that can be written to a Micropython Framebuffer when on the pico.
6. Host the data in an S3 bucket.


## Step 1,Walking Skeleton

We now have a walking skeleton of a lambda function that writes a json file to an S3 bucket. We'll return once we have a Pinky function to read it.

## Step 2, fetch, downsample and prepare river data.

We need to fetch the raw data, available as a CSV, for the two river monitoring points, downsample it (from 400-ish data points to exactly 200) using the Three buckets largest triangle algorithm. Add in a little metadata, and combine it into a single json file. We're not plotting any graphs now, but will use the data later.

Because we love encapsulation and single responsibility, we'll have a new Python file that does the fetching (or loading) of the data, resampling (by calling out to LTTBalrithm.py) and create a JSON file. Even within in this file we'll seperate the concern of fetching from the web (or loading from file) from the concern of resampling and creating the JSON document.

A config file will have a section for each river monitoring point, with the following properties:
- name
- url
- "Top of normal range" (height in meters)
- "Highest ever recorded" (height in meters)
- y-axis top (just so the y-axis of the graph has a little headroom, and ends on a round number)

For each River monitoring station we will:
- Fetch the csv files from the web (or local file for test), keep them in memory, no need to save them at this point.
- Downsample the data to 200 data points using the LTTB algorithm.
- Add the values from the config (name, top of normal range, highest recorded, top of y-axis, - we don't need the URL although it won't hurt to keep it.)
Add the 200 data points as a list to a json file. Just heights in meters, to a max of 2 decimal places, we don't need the time for every datapoint.
Include in the metadata the time of the first record, and the time of the last record (which will be used to label the x-axis)

We then Repeat for the second monitoring station, include as a second object in the json file.
and Write the json file to an S3 bucket (or local file for testing).

The main Lambda function will then call this new Python file, fetching data from the URL, reprocessing it, and writing this JSON to the S3 bucket (instead of Hello World).

## Step3, let's generate an image!

OK - now we get to the exciting stuff. As well as generating the JSON file and uploading it to S3, let's also generate an image and upload that too.

As always, encapsulation is king, so a new Python file is in order. We'll pass the JSON data (not the file, we still have it in memory, so we'll just pass it in).

Then we'll generate a 400x300 pixel .png image. White background with black text. And we'll include time, formatted to be human readible, from the top of the JSON data. That's enough for now.

We'll save this new png file to the S3 bucket (or local file for testing) and call it something like "latest.png"