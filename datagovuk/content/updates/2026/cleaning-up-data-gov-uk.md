---
title: The National Data Library – cleaning up data.gov.uk
date: 2026-11-11
summary: How we reduced broken links on data.gov.uk from over 30% to about 7% as we build the National Data Library.
authors:
  - Joe Lanman
  - Antonia Panayotova
image:
  src: images/updates/cleaning-illustration-16-9.png
  alt: Isometric illustration of a swarm of robot hoovers
---

The National Data Library (data.gov.uk) helps people find and use open data from across the UK public sector. We link to data published by public sector organisations rather than holding it centrally.

Over the years, as teams focused on other priority services, broken links had built up on data.gov.uk. This was a poor user experience, so cleaning them up was our main priority when we started transforming the service.

Working with data publishers, we’ve removed 60,818 broken links so far and fixed others, bringing broken links down from over 30% to about 7%.

## Why so many broken links?

data.gov.uk launched in 2010, and a lot has changed in 16 years! In many cases the data is simply not available any more. Reasons vary but some examples are:

- organisations, such as NHS trusts or local councils, closing or merging and taking their websites offline
- commercial data hosting providers closing and going offline
- data being republished elsewhere without older links being updated or removed

Tim Berners-Lee (inventor of the web and co-founder of data.gov.uk) wrote a classic essay – [Cool URLs don’t change](https://www.w3.org/Provider/Style/URI). In some cases, old links were redirected to the data’s new location, and files were archived before removal, but it does not always happen. However, many older versions of government websites are available in the [UK Government Web Archive](https://webarchive.nationalarchives.gov.uk).

data.gov.uk previously had a policy of keeping links to datasets that have been removed, to aid historical records. But we know from feedback and research that clicking broken links was easily the biggest issue our users faced. With The National Archives providing a robust archive of government sites, this means we can focus on providing useful and usable data in the National Data Library and remove old broken links.

## Finding broken links

In June 2026, we ran automated tests on 250,260 links from 51,203 datasets. We found 89,217 links had possible errors and divided them into two groups.

45,681 errors we were more confident about, like:

- 404 – the [HTTP status code](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status) meaning ‘not found’
- 410 – gone
- DNS failures or the server connection failed

43,536 errors we were less confident about and needed more investigation:

- 403 – can mean you need to sign in, or that the server is blocking you
- Connections that timed out without a response
- 400 – a problem with the request, such as an API request missing a required parameter
- 500 – server error
- 429 – too many requests sent at once

## What we did about it

The National Data Library is public infrastructure, so we needed to be very careful about how we clean up broken links to provide a better experience for users.

We contacted affected data publishers about their links and got really helpful responses. We were pleasantly surprised by the warm welcome and excitement that there’s a team back on data.gov.uk! In some cases, publishers updated their links, in others they confirmed that the data was gone. Some publishers have asked for more time to check, especially where their data catalogues are quite large.

We’d like to thank all the data publishers who worked with us to help us clean up broken links!

During the process we refined our automated testing methods and added [Playwright](https://playwright.dev/) fallback to test with a real browser when we weren’t sure if a link is truly broken. We also did manual testing to build on our analysis of the broken links we were less confident about – for example some sites prevent automated checking through bot detection.

We built a dashboard tool so we can better understand the status of links on the National Data Library and send publishers the data they need to resolve issues.

![Screenshot of the National Data Library Explorer dashboard, showing a table of links with their status, dataset, publisher and whether they were harvested. Filters on the left show 205,684 links with an OK status and 15,564 with errors, and the number of links for each publisher.](images/updates/explorer-links.webp)

Another issue users have highlighted is that data.gov.uk allows datasets with no links (for example if a dataset is planned but the data is not yet released). So we added a new search filter which by default only shows datasets with links. We’ll be monitoring how people use the filter to understand whether datasets without links are valuable to users.

## Next steps

We’ll continue to work closely with publishers on cleaning up remaining broken links.

We’re also continuing to transform the fundamentals of the service that matter to users, from how data listings get published to how they can be discovered and understood.

For example, about 80% of listings are published through automated ‘harvesters’ from other sites. The way these harvesters currently work is significantly limiting, for example in how accurately we can convey key details such as creation and updated dates. We’ve started work to redesign harvesters from the ground up and build in useful features such as link validation.

You can read more in our [roadmap for the National Data Library](https://www.data.gov.uk/roadmap/) which we updated in October.
