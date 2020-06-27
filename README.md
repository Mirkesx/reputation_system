# User-Reputation over Twitter

<h3>Introduction</h3>

Whoever nowdays has been signed on at least one social network. They really changed how we perceive reality and even the way we interact with each other. 

Because of them, there is one thing which is really important for users and companies to have: a really good reputation online. It can really determine the success or the failure of any type of work or social project.

With this repo, i want to give you a way to get to know more about the reputation-system studying how twitter users interact with public pages such as politics' or companies'. It will show you how to use lot of the most recent technologies to interact with Big Data in a real time scenario using little Machine Learning by performing sentiment analysis on the data we gather.

<h3>What do you need?</h3>

To run all the software you must have <b>Docker</b> installed on your machine. You can surely install all the softwares one by one locally on your machine, but with docker it is way easier both to getting started and to change/fix stuff.

You have no restriction about OS, but surely UNIX machines will have way easier life to get Docker running. You can still use Windows using WSL 2.

You will need around <b>5/7 GB</b> to install all the stuff, but consider to have at least 10/15 GB in total because you will need space to store all the tweets you will gather using this software.

Lastly you need Twitter dev keys to scrap tweets. You can get them by sign in at this website: https://developer.twitter.com/en.

<h3>Project highlights</h3>

<img src="https://github.com/Mirkesx/tap-progetto/blob/master/images/tap-progetto.png">

We will use Twitter as our source. Since we want to gather tweets in real-time, <b>Flume</b> will be our way to gather all this raw data without losing any of them. Two servers (<b>ZooKeeper and Kafka</b>) will handle the streaming of this data to <b>Spark</b> which will model this data into special json objects and which will filter tweets we don't need. Spark will perform sentiment analysis too to understand if a tweet is negative or positive.

Lastly <b>Elastic Search</b> and <b>Kibana</b> are used to index all these json objects and show particular statistics which can tell how much high is the reputation of a particular user over time.

<h3>How to use the software</h3>

Open a terminal and go into /bin folder then type:

- bash progettoESKibanaStart.sh
- bash progettoServersStart.sh
- bash proggettoCreateTopic.sh [topic]

Those will start the elastic-serach/kibana environment and the kafka e zk servers. In the third command you have to specify a topic (Kafka uses topic to stream data) which is a word you can choose freely. Just remember it since we will need it after this step.

Once you did both command you can open a browser and reach the url localhost:5601 to open kibana's client. It is time now to start flume and spark streaming so open two terminals and on each one type one of the following commands:

- bash progettoFlumeStart.sh [topic] [keywords]
- bash progettoSparkStart.sh [topic] [usernames] [user_ids]

So yuo can probably see that you need to type the same word you used previously for the topic, but what about the other args?

The keywords for flume must be a list of words (all written into "" and separated by commas) which must contain words you want to use to filter tweets before streaming them. It is not mandatory, but a good advice would be to use the twitter usernames as keywords.

Speaking of spark, you must set the topic (same as flume and kafka servers) and you must specify at least one Twitter username. If you want to specify more than one username you have to write them inside "" and separated by spaces. IDS are not mandatory so you can skip them if you want.

You will understand that all of this is working if you will start seeing text streaming on the terminal where you started spark.

We are almost done! Now you need to specify an index for the kibana client.

By default you have an index, but first i'll show you how to create a new one. If you want to keep the default just skip this part.

<img src="https://i.ibb.co/z7mF7L6/image.png">

Go to Management > Kibana > Index Patterns and click on <b>Create index pattern</b>.

<a href="https://ibb.co/DD321w6"><img src="https://i.ibb.co/VWX4LMh/image.png" alt="image" border="0"></a>

Then type "twitter" and click on <b>Next Step</b>. Choose timestamp on the select menu and click <b>Create index pattern</b>.

If you want to use the default index, you have to go to the "twitter" index you already have and open it. Then press "Refresh".

Now that you have it, you can start building up your Dashboard adding Visualizations. You can find more examples on how to do so on the references on the bottom of this page.

If you want now to stop the software you must press CTRL+C on both the terminals where you started flume and spark (or kill those processes) and then run these commands to stop elastic-search/kibana and the kakfa/zk servers:

- bash progettoESKibanaStop.sh
- bash progettoServersStop.sh

Eventually you can decide to delete all the volumes of Kafka and ZK servers by using this command:

- bash progettoDeleteKafkaVolumes.sh

<h3>References</h3>

About WSL 2: https://docs.microsoft.com/it-it/windows/wsl/wsl2-index

About Kibana Visualizations: https://www.elastic.co/guide/en/kibana/current/visualize.html

