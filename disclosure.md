# Disclosure Statement:

I sought assistance from a LLM for this project. I explicity specified that I did not want it to provide direct answers or code. I instead used it for guidance when I became stuck. A problem I ran into frequently was syntax related issues with `regex`. 

As an example, the following is an excerpt of output from a query I made on claude.ai:

> You're on the right track with the structure — 
regex for IP addresses is one of those ones that's genuinely tricky to figure out from scratch. 
Let me give you a hint rather than the answer.
An IPv4 address is just four groups of numbers separated by dots. 
Each group is 1-3 digits. In regex:

>> `\d{1,3}` matches 1 to 3 digits
>> `\.` matches a literal dot

> So you need four of those groups with dots between them. 
> Give it another shot with that in mind — how would you chain those pieces together?
