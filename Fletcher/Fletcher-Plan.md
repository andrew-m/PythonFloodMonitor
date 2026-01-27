
# Fletcher - (the Data Fetcher!) - Detailed plan

### this is what we know from the ../plan.md 
Fletcher will be written in python, to run in an AWS lambda function or locally on a Macbook (or any regular computer, but a Mac's what I have).
It will itself be neat and tidy with encapsulation and seperation of concerns.

Eventually (not yet) Fletcher will:

0. Be defined in AWS using infra-as-code written in Terraform. 
1. Fetch the data from the environment agency website (or for testing, from local files).
2. Resample the data into a smaller set of data points to fit the small e-ink display. We'll do that by adapting existing code that uses the LTTB algorithm. (Largest Triangle Three Bucket).
3. Assemble an image representing the whole e-ink display, of 400x300 pixels. There will be two graphs (histograms really), one in the top left and one in the bottom left, for 2 datasets from two locations where the en "Marlow Downstream" and "Cookham Upstream". With Axes, scales, and a title. On the right will be large numbers showing the current (or most recent) values for each location.
2. Reformat the data into a file-format that can be displayed on an e-ink display. Probably a byte array that can be written to a Micropython Framebuffer when on the pico.
3. Host the data in an S3 bucket.


## Step 1,Walking Skeleton

We now have a walking skeleton of a lambda function that writes a json file to an S3 bucket. We'll return once we have a Pinky function to read it.