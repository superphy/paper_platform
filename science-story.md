# NML Science Story
Spfy: an integrated graph database for real-time prediction of bacterial phenotypes and downstream comparative analyses. Le KK, Whiteside MD, Hopkins JE, Gannon VPJ, Laing CR. 2018. Database. 
Available at: 10.1093/database/bay086

# What was known about this area prior to your work, and why was the research done?
The NML develops and utilizes whole-genome sequence (WGS) based analyses to rapidly conduct tests that have traditionally been performed by reference laboratories. We have previously developed SuperPhy (^1), a platform that pre-computed analyses of _Escherichia coli_ genomes using in-silico tests for serotype, toxin sub-type, and the presence of known virulence- and antimicrobial resistance (AMR) factors.

Prior to the current work, these predictive genomics analyses would be conducted, but they would not be stored long term, or in a way that facilitated their reuse, meaning the same analyses would often have to be re-computed for the same genomes. 

The purpose of this project, named Spfy, was to create a flexible graph database, capable of integrating results from new and continued analyses, using standardized metadata ontologies. This will allow it to support downstream comparative analyses using stored results, in combination with the analyses of new genomes or analyses methods.

# What are your most significant findings from this work?
Spfy is provided as a web interface at https://lfz.corefacility.ca/superphy/spfy/ and implements a graph database for long-term data storage. It can accommodate new analysis software modules as they are developed, and easily link new results to those already stored. Spfy provides a storage and analyses approach that is able to match the rapid accumulation of WGS data in public databases. Initially, 10,243 _E. coli_ genomes were analyzed and used as a demonstration for the database, but in future it can be expanded to other species such as _Salmonella_.

For downstream comparative analyses, any form of metadata may be used, including the presence or absence of genomic regions, serotype, toxin-subtype, location or host-source. For example, a user could ask what genomic regions differed significantly between genome of serotype O157:H7 and serotype O26:11, and be presented with results within 2-3 minutes.

# What are the implications or impact of the research?
The integrated approach taken in Spfy, where the analyses, storage, and retrieval of results is combined, provides enormous benefits for the large-scale analyses of bacterial genomes. The developed analyses modules are also self-contained and can be used in existing platforms such as Galaxy.

Such long-term integration will help facilitate inferences about individual strains, such as the pathogenicity of a particular isolate in an outbreak situation, in addition to inferences about changes at the population level, such as the identification of emerging pathogens through routine surveillance activities. Ultimately, Spfy should reduce the re-computation of analyses, leading to faster and more comprehensive insights into bacterial pathogens, ideally leading to a reduction in the burden of illness for Canadians.

# Additional References of Significance
[^1] Whiteside MD, Laing CR, Manji A, Kruczkiewicz P, Taboada EN, Gannon VPJ. SuperPhy: Predictive genomics for the bacterial pathogen Escherichia coli. BMC Microbiology. 2016;16:65. doi:10.1186/s12866-016-0680-0.

Whiteside MD, Gannon VPJ, Laing CR. Phylotyper: in silico predictor of gene subtypes. Bioinformatics. 2017; May:0–3. doi:10.1093/bioinformatics/btx459.

