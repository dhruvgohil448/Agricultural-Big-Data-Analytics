# Project Execution & Web Interface Links Rule

Whenever the user asks to run, start, or launch the project (e.g., "run the project", "start the project", "open hadoop"):
1. Ensure the required services are active:
   - Streamlit dashboard: `http://localhost:8501`
   - Hadoop HDFS NameNode / DataNode (`localhost:9870`)
   - YARN ResourceManager (`localhost:8088`)
2. ALWAYS provide the complete list of clickable links:
   - **Streamlit Analytics Dashboard**: [http://localhost:8501](http://localhost:8501)
   - **HDFS File Explorer (Project Dir)**: [http://localhost:9870/explorer.html#/user/dhruvgohil/agriculture](http://localhost:9870/explorer.html#/user/dhruvgohil/agriculture)
   - **HDFS NameNode Overview**: [http://localhost:9870](http://localhost:9870)
   - **YARN Cluster Manager**: [http://localhost:8088/cluster](http://localhost:8088/cluster)
3. If requested or appropriate, open them directly using `open <url>` on macOS.
