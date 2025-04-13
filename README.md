# A propotype for engaging LLM for natural language to SQL generation 

And yes, Couchbase let's you run SQL with JSON saved at backend. 


## Setup 

Run [Couchbase](https://hub.docker.com/_/couchbase) docker image for a fast local setup. 

Then download the [travel-sample](https://docs.couchbase.com/server/current/manage/manage-settings/install-sample-buckets.html) sample bucket.


## How it's done 

![image](https://github.com/user-attachments/assets/3cceceb4-5e0d-4c39-8e81-42ce73b239a0)


## Test Run

Run app.py to start getting answers on your data.

Ask couple of relevant questions first. Look at the sample documents for ideas. Check out the logs for more details. 

![image](https://github.com/user-attachments/assets/352301d3-689f-422c-a477-295f2e464f85)

Here are some questions that worked for me: 

**"How many hotels are there in our database?"**

For JOINs:

**"Give me the names of airline that operates flight from JFK airport"**

Try also ask irrelevant questions! 

**"Who's Bruce Lee?"**

