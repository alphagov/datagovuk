---
title: The National Data Library roadmap
---

This roadmap sets out our priorities and direction for the National Data Library as of October 2026. Our roadmap is split into:

- 'Now' for work that's underway
- 'Next' for areas we plan to explore once current work is near complete
- 'Later' for our long-term direction - at this stage, these are aims rather than confirmed commitments

Our priorities may change as we learn more about what our users need. We've included a feedback form across the website where you can [tell us what you think and inform our future plans](https://forms.office.com/e/9V26PNFQaR).

We began transforming data.gov.uk into the National Data Library in February 2026. You can read about [what we've delivered so far](#done) at the end of this page.

You can also see and comment on upcoming curated data pages on our [GitHub repository](https://github.com/alphagov/datagovuk/issues). The repository is open, but you will need a GitHub account to comment.

We'll update this roadmap at least every 6 months as part of our commitment to working in the open.

# Now

Evidence over the last 6 months shows that users find the new curated collections a useful starting point for exploring public sector data. The next step is to build on their success and make sure the service works well at a larger scale.

The current platform is over 10 years old and its technology limits what we can offer. We're setting up a modern, sustainable service that makes data easy to find and use.

## Search

We're rebuilding the website's search so that it helps you find the most useful and up-to-date data for your needs across all the data on the website.  We are making sure our new search matches how people look for data: by topic, location, time period or format.

## A more reliable platform

We're moving to a modern and reliable technical platform. For you, this means a faster, more stable service. For us, it means we can add new features and fix problems quickly. To make our service more reliable, we are:

- moving to an updated hosting infrastructure
- running security and performance testing to find and reduce errors
- upgrading the systems that store and serve data

## Growing curated content

We continue to add new data and visualisations to curated collections. We also continue to improve existing pages based on user feedback. You can help us by [suggesting data which meets our data curation principles](https://www.data.gov.uk/data-curation/).


## Automated publisher experience

We want to make it easier and more reliable for our data publishers to publish data on the service. We're redesigning how data gets added and updated, with the aim of providing richer information about the data published to users.

We are currently focusing on data published in an automated way via harvesters. Harvested data makes up the majority of data on the service. Previously, this was done through an extension of CKAN. CKAN is an the open-source system that manages published data in the background. 

Harvesting through CKAN has limited the accurate metadata we can collect from publishers, which in turn can make data harder to find for users. We are testing new ways to automate publishing which are easy for publishers to use and can collect rich metadata to help users find the right data.

## Accessibility

We want the service to work well for everyone. We completed a full external accessibility review in September. We are now fixing the issues we found.

# Next

## Extending curated collection structures

As we add more curated data, we need to make sure collections are still easy to browse. We're designing how the pages and their components, such as individual datasets and APIs, remain easy to navigate. this includes improving links to related data as the volume of curated data grows. 

## How APIs are presented

Some datasets are available through APIs and more are being added. Our user reserach shows many users want to access data via APIs. It also shows our service makes data APIs hard to find. We plan to make it easy to find and understand how to use data APIs.

## Other parts of the publisher experience

We aim to improve the manual publishing experience and overall end-to-end journeys for publishers. The aim is to make it easier for publishers to share rich information and for users to find data.

## Data manual improvements

We want to test a new version of the data manual. We want to go beyond listing important guidance and frameworks, and create an easy-to-read guide to how the public sector does data.

# Later

## Becoming the trusted gateway to high-quality public sector data
As the trusted gateway to public sector data, we'd like to:

- help users navigate different types of public sector data, beyond open data
- find out what data is in demand and how we might help make it available
- make relationships between datasets clearer - this may include enriching metadata and experimenting with user-generated metadata

## Stronger foundations for reuse
Finding data is only the first step. We'd like to:

- explore interoperability with other data services
- test way to encourage reuse through real-world examples, reusable tools and code, safe spaces to experiment with data, and AI features 
- run community challenges that bring people together to solve real problems with data


# Out of scope
The following are not part of the scope of this work at the moment:

- Replacing specialist or departmental data services
- Mandating data publication or standards across government
- Providing data exchange tools
- Providing a data hosting solution

# Done

From February to August 2026, we started the service redesign  testing new features and fixing the most pressing problems with the existing service.

## Introducing curated data collections

We selected some of the UK's most widely used public datasets and organised them into themed collection pages. Each page explains what the data covers, who publishes it and how to access it. You can read more about [the criteria we consider when curating data](/data-curation) for the collections. 

We published over 70 collection pages across 7 themes, including environment, business and economy, transport and land and property. We also tested and iterated data visualisations to help service users understand the data at a glance.

## Introducing the data manual

We brought together guidance on managing, sharing and using public sector data into a single place called the 'data manual'.

## Directory improvements

The original data directory went without regular maintenance for several years. This led to broken links and out-of-date content. We identified the most significant problems and:

- removed over 60,000 broken links 
- hid pages without data links behind a filter, so that serach results show you data which is available
- resolved errors with automatic harvesters from key other services
- fixed backend errors to make the service faster and more stable

## Working in the open

We started sharing our plans and progress publicly. This is so that you can see what we're doing and tell us what you think. To work in the open, we have:

- published this roadmap and our data curation process
- set up user feedback forms and metrics and effective ways to monitor service performance
- completed our first baselining survey to understand user experiences priorr to transformation
- completed benchmarking reserach 6 months after to understand any changes in user satisfaction
