# ml-git: architecture and internals #

## metadata & data decoupling ##

The first design concept about ml-git is to decouple the ML entities metadata management from the actual data such that there are 2 main layers in the tool:
1. the metadata management : There are for each ML entities managed under ml-git, the user needs to define a small specification file. These files are then managed by a git repository to retrieve the different versions.
 
2. the data store management

| <img src="/blob/master/docs/mlgit-metadata-data.png?raw=true" height=223 width=600 alt="mlgit-metadata-data"> |
|:--:|
| *Figure 1. Decoupling Metadata & Data Management Layers* |


### Content Addressable Storage for ml-git ##

ml-git has been implemented as a Content Addressable Storage, meaning that we can retrieve the information based on the content and not based on the location of the information.

| <img src="/blob/master/docs/cidv1.png?raw=true" height=300 width=1200 alt="mlgit-cidv1"> 
|:--:|
| *Figure 2. self-describing content-addressed ID* |

Figure 2. shows the basic principle of multihash to obtain a CID which are used under the hood by ml-git to implement its content addressable storage layer.

In a nuthsell, CID, self-describing content-addressed ID enables natural evolution and customization over simple and fixed cryptographic hashing schemes.
As an argument why multihash is a useful feature, is that any cryptographic function ultimately ends being weak. As en example, when collisions have been proven with SHA-1, it's been a challenge for many softwares to use another cryptographic hash (including git).

Summarizing, a CID is :
* a unique identifier/hash of “multihash” content.
* encoding the digest of the original content enabling anyone to retrieve thatcontent wherever it lies (through some routing)
* enabling the integrity check of the retrieved content (thx to multihash and the encoded digest)

| ![mlgit-cidv1](IPLD-CID.png) |
|:--:|
| *Figure 3. IPLD - CID for a file* |

There are a few steps to chunk a file to get an IPLD - CID format:
1. slide the file in piece of, say, 256KB
2. for each slice, compute its digest (currently, ml-git uses sha2-256)
3. obtain the CID for all these digests. These slice of files will be saved in a data store with the computed CID as their filename. 
4. build a json describing all the chunks of the file
5. obtain the CID of that json. That json will also be saved in the data store with the computed CID as its filename.

Note that this last CID is really the only piece of information you need to keep to retrieve the whole image.jpg file.
And last but not least, one can ensure the integrity of the file while downloading by computing the digests of all downloaded chunks and checking against the digest encoded in their CID.

Follow the links below for more information on
* [multihash](https://github.com/multiformats/multihash) 
* [CID](https://github.com/multiformats/cid)
* [IPLD](https://github.com/ipfs/js-ipfs/tree/master/examples/traverse-ipld-graphs)

### Why slicing files in chunks? ###

IPFS uses small chunk size of 256KB … Why?

* __security__ - easy to DOS nodes without forcing small chunks
* __deduplication__ - small chunks can dedup. big ones effectively dont.
* __latency__ - can externalize small pieces already (think a stream)
* __bandwidth__ - optimize the use of bandwidth across many peers
* __performance__ - better perf to hold small pieces in memory. hash along the dag to verify integrity of the whole thing.

the big DOS problem with huge leaves is that malicious nodes can serve bogus stuff for a long time before a node can detect the problem (imagine having to download 4GB before you can check whether any of it is valid). this was super harmful for bittorrent (when people started choosing huge piece sizes), attackers would routinely do this, very cheaply-- just serve bogus random data. smaller chunks are very important here.



## ml-git high-level architecture and metadata ##

| ![mlgit-arch-metadata](ml-git--architecture-and-metadata.png) |
|:--:|
| *Figure 4. ml-git high-level architecture and meta-/data relationships* |

So IPLD/CID has been implemented on top of the S3 driver.
The chunking strategy is a recommendation to turn S3 interactions more efficient when dealing with large files.
It's also interesting to note that if ml-git implements a Thread pool to concurrently upload & download files to a S3 bucket.
Last but not least, it would be possible to further accelerate ml-git interactions with a S3 bucket thanks to AWS CloudFront. (not implemented yet)

### ml-git baseline performance numbers ###

#### CamSeq01 under ml-git  ####

* CamSeq01 size : 92MB
* Locations: website in Cambridge -- S3 bucket in us-east-1 -- me in South Brazil

* Download from website: ~4min22s

* upload to S3 with ml-git :
    * Sequential : 13m24s
    * Concurrent (10 threads) : 6m49s
    * Concurrent (20 threads) : 4m29s
* download to S3 with ml-git :
    * Sequential : 7m21s
    * Concurrent (10 threads) : 1m11s
    * Concurrent (20 threads) : 0m51s

#### MSCoco (all files) under ml-git  ####

* MSCoco :
    * Size : 26GB
    * number of files : 164065 ; chunked into ~400-500K blobs (todo: exact blob count)
* Locations: original dataset: unknown -- S3 bucket in us-east-1 -- me in South Brazil

* Download from website: unknown

* upload to S3 with ml-git :
    * Concurrent (10 threads) : 12h30m
* download to S3 with ml-git :
    * Concurrent (10 threads) : 10h45m

#### MSCoco (zip files) under ml-git  ####

* MSCoco :
    * Size : 25GB
    * number of files : 3 (train.zip, test.zip, val.zip) ; 102299 blobs
* Locations: original dataset: unknown -- S3 bucket in us-east-1 -- me in South Brazil

* Download from website: unknown

* upload to S3 with ml-git :
    * Concurrent (10 threads) : 4h35m
* download to S3 with ml-git :
    * Concurrent (10 threads) : 3h39m

## ml-git add, commit, push commands internals ##

| ![mlgit-command-internals](ml-git--command-internals.png) |
|:--:|
| *Figure 5. ml-git commands internals* |





