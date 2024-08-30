#!/usr/bin/env python3
"""Flow Log Parser and Analyzer.

This script defines a FlowLogMapper class that parses flow log data and maps
each row to a tag based on a lookup table. It generates an output file containing
both tag counts and port/protocol combination counts.
"""

import csv
import logging
import sys
import argparse
from typing import Dict, Tuple, Optional

class FlowLogAnalyzer:
    """A class to analyze flow logs and generate reports."""
    # Additional protocols can be added  here or using external file
    # For this implementation I will use tcp udp and icmp
    # Constants
    PROTOCOL_MAP = {6: 'tcp', 17: 'udp', 1: 'icmp'}

    def __init__(self, log_file: str, lookup_file: str, output_file: str):
        """Initialize.

        Args:
            log_file: Path to the flow log file.
            lookup_file: Path to the lookup table CSV file.
            output_file: Path to the output file for analysis results.
        """
        self.log_file = log_file
        self.lookup_file = lookup_file
        self.output_file = output_file

        self.lookup_table: Dict[Tuple[str, str], str] = {}
        self.tag_counts: Dict[str, int] = {}
        self.port_protocol_counts: Dict[Tuple[str, str], int] = {}

        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def load_lookup_table(self) -> None:
        """Load the lookup table from a CSV file."""
        try:
            with open(self.lookup_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) == 3:
                        dstport, protocol, tag = row
                        self.lookup_table[(dstport.lower(), protocol.lower())] = tag  # Preserve tag case
                logging.info("Loaded %d entries from the lookup table.", len(self.lookup_table))
        
        # error handling
        except FileNotFoundError:
            logging.error("Lookup table file not found: %s", self.lookup_file)
            raise

        except PermissionError:
            logging.error("Permission denied when reading lookup table: %s", self.lookup_file)
            raise

        except csv.Error as e:
            logging.error("Error parsing CSV file: %s", e)
            raise

    def _process_line(self, line: str) -> Optional[Tuple[str, str, str]]:
        """Process a single line of the flow log.

        Args:
            line: A single line from the flow log file.

        Returns (Optional):
            A tuple containing the destination port, protocol, and tag if the line is valid.
            None if the line is invalid or cannot be processed.
        """
        fields = line.strip().split()

        ## modify this line if skipping these invalid lines are not required
        if len(fields) < 14 or fields[-2] != 'ACCEPT' or fields[-1] != 'OK':
            logging.warning("Skipping invalid line: %s", line.strip())
            return None
        dstport = fields[6]
        protocol = self.PROTOCOL_MAP.get(int(fields[7]))

        if protocol is None:
            logging.warning("Unknown protocol number: %s. Using raw value.", fields[7])
            protocol = str(fields[7]).lower()
        else:
            protocol = protocol.lower()

        key = (dstport, protocol)
        tag = self.lookup_table.get(key)

        # Update counts
        self.port_protocol_counts[key] = self.port_protocol_counts.get(key, 0) + 1
        if tag:
            self.tag_counts[tag] = self.tag_counts.get(tag, 0) + 1
        else:
            self.tag_counts['Untagged'] = self.tag_counts.get('Untagged', 0) + 1

        return dstport, protocol, tag if tag else 'Untagged'

    def process_flow_logs(self) -> None:
        """Process the flow log file and populate tag and port/protocol counts."""
        try:
            line_count = 0
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    result = self._process_line(line)
                    if result:
                        line_count += 1

            logging.info("Processed %d lines from the flow log.", line_count)

        except FileNotFoundError:
            logging.error("Flow log file not found: %s", self.log_file)
            raise

        except PermissionError:
            logging.error("Permission denied when reading flow log: %s", self.log_file)
            raise

    def write_output(self) -> None:
        """Write both tag counts and port/protocol combination counts to the output file.

        Raises:
            PermissionError: If there's no write permission for the output file.
        """
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write("Tag Counts:\n")
                f.write("Tag,Count\n")
                for tag, count in self.tag_counts.items():
                    f.write(f"{tag},{count}\n")
                f.write("\nPort/Protocol Combination Counts:\n")
                f.write("Port,Protocol,Count\n")
                for (port, protocol), count in self.port_protocol_counts.items():
                    f.write(f"{port},{protocol},{count}\n")
            logging.info("Analysis results written to %s", self.output_file)
        
        except PermissionError as e:
            logging.error("Permission denied when writing to output file: %s", e)
            raise

    def run_analysis(self) -> None:
        """Run the complete flow log mapping."""
        try:
            self.load_lookup_table()
            self.process_flow_logs()
            self.write_output()
            logging.info("Analysis completed successfully.")
        
        except (FileNotFoundError, PermissionError, csv.Error) as e:
            logging.error("An error occurred:%s", e)
            raise


def main() -> None:
    "Main"
    parser = argparse.ArgumentParser(description="Flow Log Analyzer")
    parser.add_argument("log_file", help="Path to the flow log file")
    parser.add_argument("lookup_file", help="Path to the lookup table CSV file")
    parser.add_argument("output_file", help="Path to the output file for analysis results")
    args = parser.parse_args()

    try:
        analyzer = FlowLogAnalyzer(args.log_file, args.lookup_file, args.output_file)
        analyzer.run_analysis()

    except Exception as e:
        logging.error("Analysis failed: %s", e)
        sys.exit(1)


if __name__ == '__main__':
    main()
