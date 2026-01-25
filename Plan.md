# Python Flood Monitor

A project to fetch River Thames flood data from the environment agency website, reformat and host that data as an image in AWS, and then further code to fetch and display that image on a waveshare e-ink display driven by a Raspberry Pi pico.

The project will have two main components:
1. A lambda function that fetches the data from the environment agency website and hosts it in AWS. Along with infra-as-code to create the lambda function and schedule it to run every 15 minutes. The data will be hosted in an S3 bucket, and available via a public URL on a website that I already host.
We'll call this sub-project - "Fletcher" (because it sounds a bit like Data Fetcher, or Dexter Fletcher).
2. A Raspberry Pi pico that fetches the data from AWS and displays it on a waveshare e-ink display. There will be two varients, for a 2 colour black and white display, and a 3 colour display (black, white, and red).
We'll call this sub-project - "Pinky" because it's a silly shortening of "inky-pico-display" that's easy to type.

### Rules of engagement and working style.
Both components will be in the same git repository.
We will use trunk based development, no crufty long lived feature branches or tags.
We will only work on one sub-project at a time. A single git commit will only touch one of the components, never both.
Where a feature requires changes to both components we will use the "expand and contract" pattern, eg we'll add the new feature to the Data Fetcher first, then add the new feature to the inky-pico-display to consume that feature.
To support this, inky-pico-display will be tolerant, ignoring extra data it is not expecting, and continue to work successfully.

We may use branches for Experiments and Spikes, where we explore how to solve a problem, such as efficient data transfer between the Data Fetcher and the inky-pico-display. Some of these experiments can be done locally on my laptop with a connected raspberry pi pico and waveshare e-ink display. Others may require AWS and deploying the lambda function to test.

We will minimise imported dependencies. Preferring core Python libraries or code we have written ourselves. You will always check and ask permission before importing a new library that is not core python.


### End to end, Hello World, walking Skeleton!

Before we build much (any) real functionality. We'll build a walking skeleton the works end to end from AWS to the Raspberry Pi Pico.

The Fletcher-walking-skeleton will be a lambda function (that we can also invoke locally from the command line for testing) that we can deploy to AWS, that just returns a hello world message and the local time. We'll build a corresponding Pinky to fetch that message from a URL and display that message on the e-ink display. Detailed instructions will be provided in the Fletcher-Plan.md file.

This will prove out our ability to define AWS infra-as-code, build, test and deploy our python code to AWS, and fetch and display data on the e-ink display.

### Fletcher - Data Fetcher.

Fletcher will be written in python, to run in an AWS lambda function or locally on a Macbook (or any regular computer, but a Mac's what I have).
It will itself be neat and tidy with encapsulation and seperation of concerns.

1. Fetch the data from the environment agency website (or for testing, from local files).
2. Resample the data into a smaller set of data points to fit the small e-ink display. We'll do that by adapting existing code that uses the LTTB algorithm. (Largest Triangle Three Bucket).
3. Assemble an image representing the whole e-ink display, of 400x300 pixels. There will be two graphs (histograms really), one in the top left and one in the bottom left, for 2 datasets from two locations where the en "Marlow Downstream" and "Cookham Upstream". With Axes, scales, and a title. On the right will be large numbers showing the current (or most recent) values for each location.
2. Reformat the data into a file-format that can be displayed on an e-ink display. Probably a byte array that can be written to a Micropython Framebuffer when on the pico.
3. Host the data in an S3 bucket.

### Pinky - Inky Pico Display.

The design of Fletcher is all about making the code on Pinky as simple as possible.
Pinky will be written in micropython, to run on a Raspberry Pi pico connected to a waveshare e-ink "Pcio-ePaper-4.2" display, with 400x300 pixels of Black, White and Red (3 colour), or the almost identical "Pcio-ePaper-4.2" display, with 400x300 pixels of Black and White (2 colour).