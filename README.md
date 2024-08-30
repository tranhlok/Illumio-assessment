# Loc Tran - Illumio Technical Assessment

## Project Description

This project implements a Flow Log Analyzer that parses AWS VPC Flow Log data and maps each log entry to a tag based on a lookup table. The analyzer generates an output file containing tag counts and port/protocol.combination counts.

## Features

- Parses AWS VPC Flow Log data (version 2 format).
- Maps log entries to tags using a provided lookup table.
- Generates tag counts and port/protocol combination counts.
- Handles large log files efficiently.
- Provides logging for process tracking and error handling.

## Design Choices and Data Structures

### Assumtions
- Flow log and output files are in .txt format; the lookup table is in .csv format.
- A valid flow log line contains 14 fields; a valid lookup table line contains 3 fields.
- Logs with log-status other than OK and actions other than ACCEPT are excluded from analysis. This behavior can be adjusted by modifying the _process_line method.
- Followed the format, the dstport and protocol fields are located at indices 6 and 7, respectively
- Protocols other than 6 (TCP), 17 (UDP), and 1 (ICMP) are processed as raw string values. This can be modified in the provided class by changing hardcoded values or parsing protocols from a file.

### Dictionary Usage

The program extensively uses Python dictionaries for efficient data storage and retrieval:

1. Lookup Table:
   - Implemented as `self.lookup_table: Dict[Tuple[str, str], str]`.
   - Key: Tuple of (destination port, protocol).
   - Value: Corresponding tag.
   - Enables O(1) average time complexity for tag lookups.

2. Tag Counts:
   - Implemented as `self.tag_counts: Dict[str, int]`.
   - Key: Tag name.
   - Value: Count of occurrences.
   - Allows for quick updates and retrieval of tag counts.

3. Port/Protocol Counts:
   - Implemented as `self.port_protocol_counts: Dict[Tuple[str, str], int]`.
   - Key: Tuple of (port, protocol).
   - Value: Count of occurrences.
   - Facilitates efficient counting of unique port/protocol combinations.

### Case Insensitivity

To ensure case-insensitive matching:
- Lookup table keys (port and protocol) are converted to lowercase during loading.
- Input data is converted to lowercase before lookup.

### Modular Design

The program is structured into several methods, each with a specific responsibility:
- `load_lookup_table()`: Loads and preprocesses the lookup data.
- `process_flow_logs()`: Parses the flow log file.
- `_process_line()`: Processes individual log lines (private method).
- `write_output()`: Generates the final output file.

This modular approach enhances readability and maintainability.

### Error Handling and Logging

Comprehensive error handling and logging are implemented to:
- Catch and report file I/O errors.
- Log progress and warnings for exceptions.
- Provide informative error messages for debugging.

## Requirements

- Python 3.7+ (Python version used to create this program).
- CSV module (built-in).
- Logging module (built-in).

## Installation
No special installation is required beyond having Python 3.7+ installed per requested by the assignment prompt. For this reason, no `requirements.txt` is needed to run the program.
## Usage
Navigate to the main folder, which is the same folder that this readme file is located.

Run the Flow Log Analyzer from the command line :
```bash
python src/flow_log_analyzer.py <log_file> <lookup_table_file> <output_file>
```
Where:
- `<log_file>` is the path to the AWS VPC Flow Log file
- `<lookup_table_file>` is the path to the CSV file containing the lookup table
- `<output_file>` is the path where the analysis results will be written

Sample run command
```bash
python src/flow_log_analyzer.py data/flow_logs.txt data/lookup_table.csv src/analysis_results.txt
```
## Input File Formats

### Flow Log File

The flow log file should be in the AWS VPC Flow Logs default format (version 2). Each line represents a flow log entry with space-separated fields. The available fields can be found in [Flow Logs Data Fields](#flow-logs-data-fields).

### Lookup Table File

The lookup table should be a CSV file with the following columns: `dstport`, `protocol`, `tag`.

## Output

The analyzer generates an output file containing:
-  `Tag Counts`: A count of matches for each tag.
-  `Port/Protocol Combination Counts`: A count of matches for each port/protocol combination.

## Flow Logs Data Fields
Flow log records default log format (only version 2) details from [`this AWS doc`](https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html):

- `version`: The VPC Flow Logs version. If you use the default format, the version is 2. If you use a custom format, the version is the highest version among the specified fields. For example, if you specify only fields from version 2, the version is 2. If you specify a mixture of fields from versions 2, 3, and 4, the version is 4.
`Parquet data type: INT_32`
- `account-id`: The AWS account ID of the owner of the source network interface for which traffic is recorded. If the network interface is created by an AWS service, for example when creating a VPC endpoint or Network Load Balancer, the record might display unknown for this field. `Parquet data type: STRING`
- `interface-id`: The ID of the network interface for which the traffic is recorded. `Parquet data type: STRING`
- `srcaddr`: The source address for incoming traffic, or the IPv4 or IPv6 address of the network interface for outgoing traffic on the network interface. The IPv4 address of the network interface is always its private IPv4 address. See also pkt-srcaddr. `Parquet data type: STRING`
-  `dstaddr`: The destination address for outgoing traffic, or the IPv4 or IPv6 address of the network interface for incoming traffic on the network interface. The IPv4 address of the network interface is always its private IPv4 address. See also pkt-dstaddr. `Parquet data type: STRING`
-  `srcport`: The source port of the traffic. `Parquet data type: INT_32`
-  `dstport`:The destination port of the traffic. `Parquet data type: INT_32`
-  `protocol`: The IANA protocol number of the traffic. For more information, see Assigned Internet Protocol Numbers. `Parquet data type: INT_32`
- `packets`: The number of packets transferred during the flow. `Parquet data type: INT_64`
-  `bytes`: The number of bytes transferred during the flow. `Parquet data type: INT_64`
-  `start`: The time, in Unix seconds, when the first packet of the flow was received within the aggregation interval. This might be up to 60 seconds after the packet was transmitted or received on the network interface.`Parquet data type: INT_64`
-  `end`: The time, in Unix seconds, when the last packet of the flow was received within the aggregation interval. This might be up to 60 seconds after the packet was transmitted or received on the network interface.
`Parquet data type: INT_64`
- `action`: The action that is associated with the traffic:
    - ACCEPT — The traffic was accepted.
    - REJECT — The traffic was rejected. For example, the traffic was not allowed by the security groups or network ACLs, or packets arrived after the connection was closed. 
    - `Parquet data type: STRING`
- `log-status`  : The logging status of the flow log:
    - OK — Data is logging normally to the chosen destinations.

    - NODATA — There was no network traffic to or from the network interface during the aggregation interval.

    - SKIPDATA — Some flow log records were skipped during the aggregation interval. This might be because of an internal capacity constraint, or an internal error.

    -  Some flow log records may be skipped during the aggregation interval (see log-status in Available fields). This may be caused by an internal AWS capacity constraint or internal error. If you are using AWS Cost Explorer to view VPC flow log charges and some flow logs are skipped during the flow log aggregation interval, the number of flow logs reported in AWS Cost Explorer will be higher than the number of flow logs published by Amazon VPC. `Parquet data type: STRING`

## Project Organization

```
├── LICENSE                         <- Open-source license if one is chosen
├── Makefile                        <- Makefile with convenience commands like `make data` or `make train`
├── README.md                       <- The top-level README for developers using this project.
├── data
├── pyproject.toml                  <- Project configuration file with package metadata for 
│                                  illumio_technical_assessment and configuration for tools like black
├── requirements.txt                <- The requirements file for reproducing the analysis environment, e.g.
│                                  generated with `pip freeze > requirements.txt`
├── setup.cfg                       <- Configuration file for flake8
└── src                             <- Source code for use in this project.
    ├── analysis_results.txt        <- Result file.
    └── flow_log_analyzer.py       <- python source file of the FlowLogMapper class.
```
--------

