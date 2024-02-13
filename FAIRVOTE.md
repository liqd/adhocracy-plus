# Fairvote Module Overview

The **fairvote** module aims to balance majority decisions with minority rights.

As an example, suppose there are 40 users that generate various ideas related to citizen concerns. Suppose that

- 60% of users (24 individuals) are from the south districts of the city;
- 40% of users (16 individuals) are from the north districts.

Each user supports only ideas related to his or her district. Therefore, initially the south-oriented ideas appear at the top:

![South Ideas Votes](https://github.com/ariel-research/adhocracy-plus/assets/73301483/267ba19e-00ef-4587-a030-182346dd3078)
![North Ideas Votes](https://github.com/ariel-research/adhocracy-plus/assets/73301483/d10bece9-caf5-4c62-a763-d2daa062e9c5)

Suppose the project manager accepts the top idea, which is south-oriented.
The **fairvote** module then gives all users the same amount of "choins" (virtual choice-coins),
and then has the supporters of the accepted idea (the southern users) "pay" their choins for the accepted idea.

The "cost" of each idea is (arbitrarily) set to 150; in the future we will allow different costs for different ideas.
Therefore, each user receives 6.25, the southerners pay all their money to fund the idea, and the northerners remain with 6.25.

As a result, the northern users have more choins, so their supported ideas jump to the top:

![South Issue Accepted](https://github.com/ariel-research/adhocracy-plus/assets/73301483/33fa1136-e6a8-4b6f-9768-1b584d3e84d6)
![North on Top](https://github.com/ariel-research/adhocracy-plus/assets/73301483/0f11620f-4c95-45be-88b8-172450e32248)

Near each idea, there are two numbers. 

* One is the total amount of money that is held by its supporters. This amount is now 100 for the northern ideas (6.25 times 16), and 0 for the southern ideas.
* The second is the amount of money that each supporter should receive, in order to attain the cost of 150. This amount is now ~3.13 for the northern ideas ((150-100)/16), and 6.25 for the southern ideas.

Within the fairvote module, you can sort ideas by 'most fair', which means an increasing order of the amount of remaining choins needed per user (the second number above).
In our example, the northern ideas need fewer choins, so they appear at the top.

Observe that the coins for all South ideas have been reset at this point:
![south-reseted](https://github.com/ariel-research/adhocracy-plus/assets/73301483/80ebf547-f9cb-476b-9283-a1baa22348de)

Suppose now that the project manager accepts a northern idea:
![North Issue Accepted](https://github.com/ariel-research/adhocracy-plus/assets/73301483/d744d94b-e4d3-4be5-a7fc-b442b1478c84)

The southern ideas are now on top:
![South on Top](https://github.com/ariel-research/adhocracy-plus/assets/73301483/2ae89a89-b884-4f3e-9665-09621ee50fbc)

Observe that the coins for all North ideas have been reset at this point:
![image](https://github.com/ariel-research/adhocracy-plus/assets/73301483/8e82f69a-9faf-42e8-9835-4e2ede679026)

