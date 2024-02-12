# Fairvote Module Overview

## Usage Example

Imagine a project with a 'fairvote' module, enabling the addition and support of ideas ('issues'). \
In this instance, we enlist 40 users for project participation and generate various ideas related to citizen concerns: \
half are 'south' issues and the remaining half are 'north' region issues.

- 60% of users (24 individuals) are from the 'south'.
- 40% of users (16 individuals) are from the 'north'.

Each user is associated with either the 'north' or 'south' area and supports all issues specific to their region:
- 24 'south' users support all 'south' issues.
- 16 'north' users support all 'north' issues.

Within the fairvote module, you can organize issues based on the 'most fair' ideas, \
determined by the smallest remaining coins needed for each user to invest. \

The top 4 'south' issues and the top 4 'north' issues can be visualized as follows:

**Top 4 South Issues:**
![South Ideas Votes](https://github.com/ariel-research/adhocracy-plus/assets/73301483/267ba19e-00ef-4587-a030-182346dd3078)

**Top 4 North Issues:**
![North Ideas Votes](https://github.com/ariel-research/adhocracy-plus/assets/73301483/d10bece9-caf5-4c62-a763-d2daa062e9c5)

Once a project manager decides to accept an idea (ideally the most fair one):

1. All project participants receive calculated remaining coins (the missing amount for each supporter to achieve the idea's coin goal).
2. The accepted idea is considered and no longer appears in the regular idea list.
3. The idea supporters' coins are reset.
4. Other issues' invested coins are updated.

In this example, when a 'south' issue is accepted, the 'south' users' coins reset, and the next 'fair' idea is a 'north' issue:

1. South issue accepted:
![South Issue Accepted](https://github.com/ariel-research/adhocracy-plus/assets/73301483/33fa1136-e6a8-4b6f-9768-1b584d3e84d6)

2. North issue now on top:
![North on Top](https://github.com/ariel-research/adhocracy-plus/assets/73301483/0f11620f-4c95-45be-88b8-172450e32248)

3. North issue accepted:
![North Issue Accepted](https://github.com/ariel-research/adhocracy-plus/assets/73301483/d744d94b-e4d3-4be5-a7fc-b442b1478c84)

4. South issue now on top:
![South on Top](https://github.com/ariel-research/adhocracy-plus/assets/73301483/2ae89a89-b884-4f3e-9665-09621ee50fbc)
