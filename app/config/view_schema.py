from app.view.asp_set import AspectSetH
from app.view.aspect import AspectH
from app.view.attr import AttrH
from app.view.colgrp import ColGroupsH

#===============================================
def defineViewSchema():
    aspects = AspectSetH([
        AspectH("view_gen", "General", "view", field = "general"),
        AspectH("view_qsamples", "Quality", "view",
            col_groups = ColGroupsH(attr = "quality_samples")),
        AspectH("view_gnomAD", "gnomAD", "view",
                col_groups = ColGroupsH(attr = "gnomAD")),
        AspectH("view_db", "Databases", "view", field = "databases"),
        AspectH("view_pred", "Predictions", "view", field = "predictions"),
        AspectH("view_genetics", "Bioinformatics", "view",
            field = "bioinformatics"),
        AspectH("view_inheritance", "Inheritance", "view",
            field = "inheritance", ignored = True),
        AspectH("_main", "VEP Data", "data"),
        AspectH("transcripts", "VEP Transcripts", "data",
            col_groups = ColGroupsH([
                ("transcript_consequences", "Transcript"),
                ("regulatory_feature_consequences", "Regulatory"),
                ("motif_feature_consequences", "Motif"),
                ("intergenic_consequences", "Intergenic")])),
        AspectH("colocated_v", "Colocated Variants", "data",
            col_groups = ColGroupsH(attr = "colocated_variants")),
        AspectH("input", "VCF", "data", field = "input",
            mode = "string")])

    aspects["view_gen"].setAttributes([
        AttrH("genes", title = "Gene(s)", is_seq = True,
            tooltip = "Gene Symbol (Ensembl classification)"),
        AttrH("hg19", tooltip = "Genetic coordinates in HG19 Assembly"),
        AttrH("hg38", tooltip = "Genetic coordinates in HG38 Assembly"),
        AttrH("worst_annotation", title = "Worst Annotation",
              tooltip = "Most Severe Consequences from the transcript"
                      + " with the worst annotation"),
        AttrH("canonical_annotation", title = "Canonical Annotation",
              tooltip = "Most Severe Consequences from canonical transcripts"),
        AttrH("refseq_transcript_canonical",
            title = "RefSeq Transcript (Canonical)", is_seq = True),
        AttrH("refseq_transcript_worst",
            title = "RefSeq Transcript (Worst)", is_seq = True),
        AttrH("ensembl_transcripts_canonical",
            title = "Ensembl Transcripts (Canonical)", is_seq = True),
        AttrH("ensembl_transcripts_worst",
            title = "Ensembl Transcripts (Worst)", is_seq = True),
        AttrH("ref", title = "Ref"),
        AttrH("alt", title = "Alt"),
        AttrH("splice_region", title = "Splice Region", is_seq = True),
        AttrH("gene_splicer", title = "GeneSplicer", is_seq = True),
        AttrH("splice_altering", title = "Splice AI splice altering"),
        AttrH("cpos_worst", title = "cPos (Worst)", is_seq = True),
        AttrH("cpos_canonical",
            title = "cPos (Canonical)", is_seq = True),
        AttrH("cpos_other", title = "cPos (Other)", is_seq = True),
        AttrH("ppos_worst", title = "pPos (Worst)", is_seq = True),
        AttrH("ppos_canonical",
            title = "pPos (Canonical)", is_seq = True),
        AttrH("ppos_other", title = "pPos (Other)", is_seq = True),
        AttrH("variant_exon_canonical",
            title = "Variant Exon (Canonical)", is_seq = True,
              tooltip = "Exon # according to canonical transcript"),
        AttrH("variant_exon_worst",
            title = "Variant Exon (Worst Annotation)", is_seq = True,
            tooltip = "Exon # according to the transcript with "
                    + "the worst annotation"),
        AttrH("variant_intron_worst",
            title = "Variant Intron (Worst Annotation)", is_seq = True,
            tooltip = "Intron # according to the transcript with "
                    + "the worst annotation"),
        AttrH("variant_intron_canonical",
            title = "Variant Intron (Canonical)", is_seq = True,
            tooltip = "Intron # according to canonical transcript"),
        AttrH("gene_panels", title = "Gene panels", is_seq = True),
        AttrH(None),
        AttrH("proband_genotype", title = "Proband Genotype"),
        AttrH("maternal_genotype", title = "Maternal Genotype"),
        AttrH("paternal_genotype", title = "Paternal Genotype"),
        AttrH("igv", title = "IGV", kind = "place",
            tooltip = "Open this variant in local IGV "
            "(https://software.broadinstitute.org/software/igv/)"),
        AttrH("ucsc", title = "View in UCSC", kind = "place",
            tooltip = "View this variant in UCSC Browser")
    ])

    aspects["view_qsamples"].setAttributes([
        AttrH("title", title = "Title"),
        AttrH("qd", title = "Quality by Depth",
            tooltip = "The QUAL score normalized by allele depth (AD) "
            "for a variant. This annotation puts the variant confidence "
            "QUAL score into perspective by normalizing for the amount "
            "of coverage available. Because each read contributes a little "
            "to the QUAL score, variants in regions with deep coverage "
            "can have artificially inflated QUAL scores, giving the "
            "impression that the call is supported by more evidence "
            "than it really is. To compensate for this, we normalize "
            "the variant confidence by depth, which gives us a more "
            "objective picture of how well supported the call is."),
        AttrH("mq", title = "Mapping Quality"),
        AttrH("variant_call_quality", title = "Variant Call Quality",
            tooltip = "QUAL tells you how confident we are that there is "
            "some kind of variation at a given site. The variation may be "
            "present in one or more samples."),
        AttrH("strand_odds_ratio", title = "Strand Odds Ratio", tooltip = ""),
        AttrH("fs", title = "Fisher Strand Bias", tooltip = ""),
        AttrH("allelic_depth", title = "Allelic Depth", is_seq = True,
            tooltip = "AD is the unfiltered allele depth, i.e. "
            "the number of reads that support each of the reported "
            "alleles. All reads at the position (including reads that "
            "did not pass the variant caller's filters) are included in "
            "this number, except reads that were considered uninformative. "
            "Reads are considered uninformative when they do not provide "
            "enough statistical evidence to support one allele over another."),
        AttrH("read_depth", title = "Read Depth",
            tooltip = "DP - is a number of times that base pair locus "
            "was read"),
        AttrH("ft", title = "FILTERs",
            tooltip = "This field contains the name(s) of any filter(s) "
            "that the variant fails to pass, or the value PASS if the "
            "variant passed all filters. If the FILTER value is ., "
            "then no filtering has been applied to the records."),
        AttrH("genotype_quality", title = "Genotype Quality",
            tooltip = "GQ tells you how confident we are that "
            "the genotype we assigned to a particular sample is correct. "
            "It is simply the second lowest PL, because it is the "
            "difference between the second lowest PL and the lowest PL "
            "(always 0).")])

    aspects["view_gnomAD"].setAttributes([
        AttrH("allele", title = "Allele"),
        AttrH("proband", title = "Proband"),
        AttrH("pli", title = "pLI", is_seq = True),
        AttrH("af", title = "Overall AF"),
        AttrH("genome_af", title = "Genome AF"),
        AttrH("exome_af", title = "Exome AF"),
        AttrH("genome_an", title = "Genome AN"),
        AttrH("exome_an", title = "Exome AN"),
        AttrH("url", title = "URL", kind = "link", is_seq=True),
        AttrH("pop_max", title = "PopMax",)])

    aspects["view_db"].setAttributes([
        AttrH("hgmd", title = "HGMD"),
        AttrH("hgmd_hg38", title = "HGMD (HG38)"),
        AttrH("hgmd_tags", title = "HGMD TAGs", is_seq = True),
        AttrH("hgmd_phenotypes", title = "HGMD Phenotypes",
            is_seq = True),
        AttrH("hgmd_pmids", title = "HGMD PMIDs",
            is_seq = True, kind = "link"),
        AttrH("omim", title = "OMIM",
            is_seq = True, kind = "link"),
        AttrH("clinVar_variants", title = "ClinVar Variants",
            is_seq = True),
        AttrH("clinVar_significance", title = "ClinVar Significance",
            is_seq = True),
        AttrH("clinvar_review_status", title = "ClinVar Review Status",
            is_seq = False),
        AttrH("num_clinvar_submitters",
            title = "ClinVar: Number of submitters", is_seq = False),
        AttrH("clinvar_acmg_guidelines", title = "ClinVar ACMG Guidelines",
            is_seq = True),
        AttrH("lmm_significance", title = "Clinical Significance by LMM"),
        AttrH("gene_dx_significance",
            title = "Clinical Significance by GeneDx"),
        AttrH("clinVar_phenotypes", title = "ClinVar Phenotypes",
            is_seq = True),
        AttrH("clinVar_submitters", title = "ClinVar Submitters",
            is_seq = True),
        AttrH("clinVar", title = "ClinVar",
            is_seq = True, kind = "link"),
        AttrH("gtex", title = "View on GTEx", kind = "place",
            tooltip = "View this gene on GTEx portal"),
        AttrH("gene_cards", title = "GeneCards",
            is_seq = True, kind = "link"),
        AttrH("pubmed_search", title = "PubMed Search Results",
            is_seq = True, kind = "link"),
        AttrH("beacons", title = "Observed at", is_seq = True),
        AttrH("beacon_url", title = "Search Beacons",
            is_seq = True, kind = "link")])

    aspects["view_pred"].setAttributes([
        AttrH("lof_score", title = "LoF Score",
            is_seq = True),
        AttrH("lof_score_canonical", title = "LoF Score (Canonical)",
            is_seq = True),
        AttrH("max_ent_scan", title = "MaxEntScan",
            is_seq = True),
        AttrH("polyphen", title = "Polyphen",
            is_seq = True),
        AttrH("polyphen2_hvar", title = "Polyphen 2 HVAR",
            is_seq = True),
        AttrH("polyphen2_hdiv", title = "Polyphen 2 HDIV",
            is_seq = True),
        AttrH("sift", title = "SIFT from dbNSFP",
            is_seq = True),
        AttrH("sift_vep", title = "SIFT from VEP",
            is_seq = True),
        AttrH("revel", title = "REVEL",
            is_seq = True),
        AttrH("mutation_taster", title = "Mutation Taster",
            is_seq = True),
        AttrH("fathmm", title = "FATHMM", is_seq = True),
        AttrH("cadd_phred", title = "CADD (Phred)",
            is_seq = True),
        AttrH("cadd_raw", title = "CADD (Raw)",
            is_seq = True),
        AttrH("mutation_assessor", title = "Mutation Assessor",
            is_seq = True),
        AttrH("sift_score", title = "SIFT score",
            is_seq = True),
        AttrH("polyphen2_hvar_score", title = "Polyphen 2 HVAR score",
            is_seq = True),
        AttrH("polyphen2_hdiv_score", title = "Polyphen 2 HDIV score",
            is_seq = True)])

    aspects["view_genetics"].setAttributes([
        AttrH("zygosity", title = "Zygosity"),
        AttrH("inherited_from", title = "Inherited from"),
        AttrH("dist_from_exon_worst",
            title = "Distance From Intron/Exon Boundary (Worst)",
            is_seq = True),
        AttrH("dist_from_exon_canonical",
            title = "Distance From Intron/Exon Boundary (Canonical)",
            is_seq = True),
        AttrH("gerp_rs", title = "GERP Score", is_seq = False),
        AttrH("conservation", title = "Conservation", kind = "json"),
        AttrH("species_with_variant",
            title = "Species with variant"),
        AttrH("species_with_others",
            title = "Species with other variants"),
        AttrH("max_ent_scan", title = "MaxEntScan", is_seq = True),
        AttrH("nn_splice", title = "NNSplice"),
        AttrH("human_splicing_finder", title = "Human Splicing Finder"),
        #AttrH("splice_ai", title = "Splice AI Max Score"),
        AttrH("splice_ai_ag", title = "Splice AI acceptor gain",
            is_seq = True),
        AttrH("splice_ai_al", title = "Splice AI acceptor loss",
            is_seq = True),
        AttrH("splice_ai_dg", title = "Splice AI donor gain", is_seq = True),
        AttrH("splice_ai_dl", title = "Splice AI donor loss", is_seq = True),
        AttrH("splice_ai", kind = "hidden"),
        AttrH("other_genes",
            title = "Gene symbols from other transcripts",
            is_seq = True),
        AttrH("called_by", title = "Called by", is_seq = True),
        AttrH("caller_data", title = "CALLER DATA")])

    aspects["_main"].setAttributes([
        AttrH("label"),
        AttrH("color_code"),
        AttrH("id"),
        AttrH("assembly_name", title = "Assembly"),
        AttrH("seq_region_name"),
        AttrH("start"),
        AttrH("end"),
        AttrH("strand"),
        AttrH("allele_string"),
        AttrH("variant_class"),
        AttrH("most_severe_consequence"),
        AttrH("ClinVar"),
        AttrH("clinvar_variants", is_seq = True),
        AttrH("clinvar_phenotypes", is_seq = True),
        AttrH("clinvar_significance", is_seq = True),
        AttrH("HGMD"),
        AttrH("HGMD_HG38"),
        AttrH("HGMD_PIMIDs", kind = "hidden", is_seq = True),
        AttrH("HGMD_phenotypes", kind = "hidden", is_seq = True),
        AttrH("EXPECTED"),
        AttrH("gnomad_db_genomes_af", kind = "hidden"),
        AttrH("gnomad_db_exomes_af", kind = "hidden"),
        AttrH("SEQaBOO")])

    aspects["transcripts"].setAttributes([
        AttrH("amino_acids"),
        AttrH("bam_edit"),
        AttrH("biotype"),
        AttrH("cadd_phred"),
        AttrH("cadd_raw"),
        AttrH("canonical"),
        AttrH("ccds"),
        AttrH("cdna_end"),
        AttrH("cdna_start"),
        AttrH("cds_end"),
        AttrH("cds_start"),
        AttrH("clinvar_clnsig"),
        AttrH("clinvar_rs"),
        AttrH("codons"),
        AttrH("consequence_terms", is_seq = True),
        AttrH("conservation"),
        AttrH("distance"),
        AttrH("domains", kind = "json"),
        AttrH("exacpli"),
        AttrH("exon"),
        AttrH("fathmm_pred"),
        AttrH("fathmm_score"),
        AttrH("flags", is_seq = True),
        AttrH("gene_id"),
        AttrH("gene_pheno"),
        AttrH("genesplicer"),
        AttrH("gene_symbol"),
        AttrH("gene_symbol_source"),
        AttrH("given_ref"),
        AttrH("gnomad_exomes_ac"),
        AttrH("gnomad_exomes_af"),
        AttrH("gnomad_exomes_an"),
        AttrH("gnomad_exomes_asj_af"),
        AttrH("gnomad_genomes_ac"),
        AttrH("gnomad_genomes_af"),
        AttrH("gnomad_genomes_an"),
        AttrH("gnomad_genomes_asj_af"),
        AttrH("hgnc_id"),
        AttrH("hgvs_offset"),
        AttrH("hgvsc"),
        AttrH("hgvsp"),
        AttrH("high_inf_pos"),
        AttrH("impact"),
        AttrH("intron"),
        AttrH("loftool"),
        AttrH("maxentscan_alt"),
        AttrH("maxentscan_diff"),
        AttrH("maxentscan_ref"),
        AttrH("motif_feature_id"),
        AttrH("motif_name"),
        AttrH("motif_pos"),
        AttrH("motif_score_change"),
        AttrH("mutationassessor_pred"),
        AttrH("mutationassessor_score"),
        AttrH("mutationtaster_pred"),
        AttrH("mutationtaster_score"),
        AttrH("polyphen2_hdiv_pred"),
        AttrH("polyphen2_hdiv_score"),
        AttrH("polyphen2_hvar_pred"),
        AttrH("polyphen2_hvar_score"),
        AttrH("polyphen_prediction"),
        AttrH("polyphen_score"),
        AttrH("protein_end"),
        AttrH("protein_id"),
        AttrH("protein_start"),
        AttrH("regulatory_feature_id"),
        AttrH("revel_score"),
        AttrH("sift_pred"),
        AttrH("sift_prediction"),
        AttrH("sift_score"),
        AttrH("strand"),
        AttrH("source"),
        AttrH("spliceregion", is_seq = True),
        AttrH("swissprot", is_seq = True),
        AttrH("transcript_id"),
        AttrH("trembl", is_seq = True),
        AttrH("uniparc", is_seq = True),
        AttrH("used_ref"),
        AttrH("variant_allele")])

    aspects["colocated_v"].setAttributes([
        AttrH("id"),
        AttrH("start"),
        AttrH("end"),
        AttrH("allele_string"),
        AttrH("strand"),
        AttrH("pubmed", is_seq = True),
        AttrH("somatic"),
        AttrH("gnomAD"),
        AttrH("frequencies", kind = "json"),
        AttrH("phenotype_or_disease"),
        AttrH("seq_region_name"),
        AttrH("clin_sig", is_seq = True),
        AttrH("minor")])

    return aspects
