# Cancer Gene Trust

The [Cancer Gene Trust (CGT)](http://ga4gh.org/#/cancergenetrust) is a decentralized 
distributed database of cancer variants and clinical data.

Stewards working directly with patient-participants publish de-identified somatic 
cancer variants and basic clinical data. Researchers who find rare variants 
or combinations of variants in this globalresource that are associated with 
specific clinical features of interest may then contact the data stewards 
for those participants.

The initial prototype implimentation leverages [IPFS](https://ipfs.io/) for 
decentralized storage and distribution, and [Ethereum](https://www.ethereum.org/) for 
authentication, authorization, and accounting.

A submission consists of a JSON manifest file containing basic de-identified 
clinical data and references to one or more [VCF](https://en.wikipedia.org/wiki/Variant_Call_Format) 
files. The manifest and VCF files are published to IPFS and the path to the manifest 
file is added to an Ethereum block chain under the Steward's account.

Maximilian Haeussler developed the initial [Ethereum contracts](https://github.com/maximilianh/acgi)
and [IPFS command line submission tool](https://github.com/maximilianh/knowledger). In addition
a simple prototype [submission web server](https://github.com/ga4gh/CGT/tree/master/cgtd) is under development.

To get involved join the discussion at the [CGT mailing list](https://groups.google.com/a/genomicsandhealth.org/forum/#!forum/ga4gh-cgt)
