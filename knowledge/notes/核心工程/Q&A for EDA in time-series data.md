我需要：1. 例子 2. 对我的问题的可能的correction 然后解答 3. 参考书本优先
Q1 : 我们使用eda 在金融数据分析中最希望达成什么事情？what is a best eda for timeseries data？ what purpose does it serve？ how do we achieve what we trying to achieve？
- A :

Q2 : 神经网络，他是statistics based吗？我看到这句话“This book is aimed at the data scientist with some familiarity with the R and/or Python programming languages, and with some prior (perhaps spotty or ephemeral) exposure to statistics. Two of the authors came to the world of data science from the world of statistics, and have some appreciation of the contribution that statistics can make to the art of data science. At the same time, we are well aware of the limitations of traditional statistics instruction: statistics as a discipline is a century and a half old, and most statistics textbooks and courses are laden with the momentum and inertia of an ocean liner. All the methods in this book have some connection—historical or methodological—to the discipline of statistics. Methods that evolved mainly out of computer science, such as neural nets, are not included.” 他最后一句，难道说 神经网络out of computer sciecne。am i asking the wrong question ？
 - A :
 
Q3 : O’Reilly 是什么？（我看的这本书）
 - A :

Q4 : 这句话让我想到的是除了这种行+列的表格形式rectangular data，还有别的形式的所谓的”data“吗？变种不俗算 Data comes from many sources: sensor measurements, events, text, images, and vid‐ eos. The Internet of Things (IoT) is spewing out streams of information. Much of this data is unstructured: images are a collection of pixels, with each pixel containing RGB (red, green, blue) color information. Texts are sequences of words and nonword char‐ acters, often organized by sections, subsections, and so on. Clickstreams are sequen‐ ces of actions by a user interacting with an app or a web page. In fact, a major challenge of data science is to harness this torrent of raw data into actionable infor‐ mation. To apply the statistical concepts covered in this book, unstructured raw data must be processed and manipulated into a structured form. One of the commonest forms of structured data is a table with rows and columns—as data might emerge from a relational database or be collected for a study
 - A :书中给出一个答案其实是 时间序列：这里的问题就是

Q4 : 我这里的问题就是逻辑上这个numeric scale 不能是special set of values 的一种吗？他的这个discrete 和 ordinal 感觉在某些例子中会从结果上比较混乱？以及只有这些是吗？给我几个例子具像化我们对于数据的这个种类分别的好处
![[Pasted image 20260802202307.png]]

 - A :
 
 Q5 : weighted mean 是不是需要 discrete 或者
 - A :
 
 Q6 : The variance, the standard deviation, the mean absolute deviation, and the median absolute deviation from the median are not equiv‐ alent estimates, even in the case where the data comes from a nor‐ mal distribution. In fact, the standard deviation is always greater than the mean absolute deviation, which itself is greater than the median absolute deviation. Sometimes, the median absolute devia‐ tion is multiplied by a constant scaling factor to put the MAD on the same scale as the standard deviation in the case of a normal dis‐ tribution. The commonly used factor of 1.4826 means that 50% of the normal distribution fall within the range ±MAD (see, e.g., https://oreil.ly/SfDk2). 解释+证明
  - A : 

Q7 : A correlation coefficient of zero indicates no correlation, but be aware that ran‐ dom arrangements of data will produce both positive and negative values for the correlation coefficient just by chance.  这句话的后半句什么意思？
-  A : 
