# Max Hoffman DCS340 Project #2- Multi-objective Evolution: Exploring Trade-offs in Biology through NSGA-II

This repository covers how evolutionary algorithms can solve problems that have competing objectives. We've covered evolutionary algorithms with a single-objective fitness function thus far, but multi-objective evolution needs to compromise between multiple peaks. 

## Why I picked this
Last summer I worked in Dr. Bavis's lab at Bates College studying the development of respiratory control in neonatal rats. My research involved exposing rat pups to various oxygen conditions and measuring their breathing patterns using head-out plethysmography. I also used temperature transponders and software such as LabChart and Prism to investigate how ventilation and metabolic responses change during neonatal development.

One of the things that interested me was how values such as breath frequency or tidal volume could change independently of one another. One rat pup may breathe more slowly but take measurably deeper breaths to reach a similar overall ventilation level consistently. Seeing this phenomenon during the data analysis processs reminded me that evolution and biological systems must to balance between meet several physiological demands simultaneously- they cannot just maximize one variable.

This idea of balancing tidal volume and frequency, or any tied biological values, also connects to material I've covered in classes like bio 202, 204, and 206. In Bio 206 we covered evolution/natural selection primarily and how envrionmental conditons influence the fitness of certain traits in an organism. Improving one trait can sometimes come at the expense of another one. In reality, fitness is not just one objective value but a combination of several.

## The main idea: pareto
One of the main ideas behind multi-objective evolution is Pareto dominance. Pareto dominance occurs when one outcome is strictly better than another for at least one person and no worse for everyone else. In the context of the neonatal rats, we have to maximize ventilation and minimize the energetic cost of breathing. 

If one rat has a higher ventilation but has to use more metabolic energy to do so- no one solution dominates the other in that case because each outperforms in one objective.

In this case, one can use the Pareto front- the Pareto front consists of all non-dominated solutions in a population. These solutions represent different compromises between objectives in cases where improving one objective would sacrifice another.

In Part A of my activity I used a hypothetical population of rat pups to demonstrate this phenomenon. Instead of identifying one best individual we found which rats were non-dominated based on balance of ventilation vs energy costs. 

The important takeaway here is that there isn't always one best answer. Sometimes there are multiple solutions that are equally valid depending on which objective is more important in the case.

## Why not just add the objectives?
At first I simply assumed that combining multiple objectives into a single fitness function like we are familar with up till this point into DCS340 would be the best approach- this is called a weighted sum.

For two objectives that we want to minimize:
Fitness = w * f1 + (1 - w) * f2

in this case, the weight determines how important each of the objectives is. By changing the weight we can prioritize different solutions.

One of the limitations I learned is that weighted sums can't identify every possible Pareto-optimal solution in every case. For example, in non-convex Pareto front cases we can't just use a weighted sum.

In Part B I investigated this idea with fronts of two different shapes: convex and concave. For convex we can change the weights to allow us to identify solutions across the curve. For the concave front the weighted sum selects solutions at endpoints so the intermediate trade-offs are missing.

This surprised me becuse the middle solutions were non-dominated but no combination of weights could select them.

This is exactly why multi-objective evolutionary algorithsm like NSGA-II are useful. Instead of combining all the objectives into one fitness value based on weight, multio objective algorithms can approximate one pareto front in a single given run.

## How NSGA-II works
NSGA-II stands for Non-dominated Sorting Genetic Algorithm II and it was first introduced in a paper written by Deb et al. in 2002.

I read this paper and I was most surprised to find that lots of the components are similar to genetic algorithms that we've already studied up to this point. In NSGA-II we still have populations, crossover then mutation and selection like the others we've covered. the primary difference is how individuals are ranked/selected when multiple objectives exist.

NSGA-II uses
1. non-dominated sorting

separates population into different Pareto fronts

The first front contains individuals that aren't dominated by others in populations- once they're removed, the algorithm identifies next non-dominated front and process keeps going

First front best: prioritizes solutions based on performance across multiple objectives

2. crowding distance

One issue with selecting non-dominated individuals is the population might cluster around a small section of pareto front

crowding distance helps to prevent this by measuring how isolated individual is from neighboring solutions for given objective

3. elitism

NSGA-II uses elitism so strong solutions can survive between genrations

After producing offspring the algorithm combines the parent and offspring populations- ranking groups together so best individuals will be selected for next generation.


I implemented these mechanisms in src/nsga2.py and my implementation uses random parent selection to simplify the code instead of tournament selection like in the NSGA paper.

I tested the algorithm using ZDT1 which is a benchmarl multi-objective optimization problem described by Zitzler, Deb, and Thiele (2000). ZDT1 is a Pareto front that we know so we can compare the colab algorithm implementation to an expected solution

## My investigations

Once I understood how NSGA-II worked, I wanted to investigate how much individual components matter. My primary question was- what happens to the quality of Pareto front when we change certain parts of NSGA-II?

I did this with ablation experiments where I changed one part of the algorithm but kept other conditions consistent.

With crowding distance I ran NSGA-II on ZDT1 using 30 variables an 100 individuals over 150 generations I found the algorithm  covered approximately 100% of the theoretical Pareto front according to the coverage measure in my experiment.

Without crowding distance the coverage dropped to only 63% and the population found 16 distinct locations to cluster around. I was surprised that both versions were still able to approach the theoretical Pareto front, genreally. What changed was how well the algorithm could maintain diverse range of good solutions.

I also tried changing population size and number of generations as well as altering the random seed (not just 42). Smaller populations and fewer generation generally limited algorithm's efficacy.

## Back to biology
I chose this topic because I wanted to connect evolutionary computing to concepts I've studied in bio.

In Bio 206 we discussed Darwin's finches and how environmental conditions can change which traits are advantageous.

Boag and Grant (1981) investigated natural selection in Darwin's finches during the 1977 drought on Daphne Major. When food availability changed and harder seeds become more important for fitness, the medium ground finches with deeper beaks developed a rapid survival advantage.

This reminded me of multi-objective optimiziation because different beak shapes can provide advantages for different tasks. Larger beaks win for hard seeds but thinner beaks are better for worms generally.

Shoval et al. (2012) investigated how evolutionary trade-offs between tasks can influence geometry of phenotype space.

Natural selection doesn't literally calculate Pareto fronts, but I think this provides an intersting way to visualize how different phenotypes could represent compromises between competing functions in biology.

## Run it yourself
| Notebook | What it does | Open |
|---|---|---|
| `notebooks/multiobjective_activity.ipynb` | In-class activity (Parts A–D) | [Colab](https://colab.research.google.com/drive/1oAwYmsKb9g5owZSzm0u06Wkf_7uAdJgf) |
| `notebooks/my_investigations.ipynb` | My ablation experiments | [Colab](https://colab.research.google.com/drive/1tBW-5Tyk9RfNbaG6p5YfoUzISGcLHmSa) |

Local: `pip install -r requirements.txt`, then open the notebooks in Jupyter.
The GitHub Actions workflow in `.github/workflows/` re-runs both notebooks on every push.

## Resources I used
- Eiben & Smith, *Introduction to Evolutionary Computing*, multiobjective chapter
- Deb et al. (2002), NSGA-II, IEEE TEC 6(2):182–197
- Zitzler, Deb & Thiele (2000), Evolutionary Computation 8(2):173–195
- Shoval et al. (2012), Science 336:1157–1160
- Boag & Grant (1981), Science 214:82–85
- Otis, Fenn & Rahn (1950), J Appl Physiol 2:592–607
- Friedman, Bavis, Kuncz, Hoffman & Bavis (2026), lab abstract

## GenAI use
Used Claude Opus 5.5 when creating this repo to help me understand the more complicated aspects of multi-objective evolutionary algorithms after reading chapter 9/12 of Eiben and Smith. I also used GenAI to help design my Colab Notebooks in a way that was interactive for peers in class to use. I used the original papers, as well as course materials and my summer research experience, to design the general setup.
