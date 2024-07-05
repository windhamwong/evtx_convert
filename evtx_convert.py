import argparse, sys, json
from evtx import PyEvtxParser
from datetime import datetime
from dataknead import Knead


def parse_arguments():
  """Parses command line arguments using argparse."""
  parser = argparse.ArgumentParser(description="Parse EVTX event log files")
  parser.add_argument("evtx_file", help="Path to the EVTX file to parse")
  parser.add_argument("-o", "--output", type=str, default=None, help="Output file path (default: stdout)")
  parser.add_argument("-f", "--format", choices=["csv", "json", "txt"], default="json",
                      help="Output format (default: json, other options: [txt, json, csv])")
  return parser.parse_args()


def main():
  args = parse_arguments()
  if args.format == 'csv' and not args.output:
    print("[-] CSV format requires an output file")
    sys.exit(1)
  file = None
  i = 0
  # Open the output file (stdout or a specified file)
  if args.output:
    if args.format != 'csv':
      file = open(args.output, "w")
    else:
      file = open("temp.json", "w")

    file.write("[\n")


  t0=datetime.now()
  parser = PyEvtxParser(args.evtx_file)
  for record in parser.records():
    if i > 0 and file and (args.format == 'json' or args.format == 'csv'):
      file.write(",\n")

    i += 1
    if args.format == "txt":
      print(f'Event Record ID: {record["event_record_id"]}', file=file or sys.stdout)
      print(f'Event Timestamp: {record["timestamp"]}', file=file or sys.stdout)
      print(record['data'], file=file or sys.stdout)
      print(f'------------------------------------------', file=file or sys.stdout)

    elif args.format == "json" or args.format == "csv":
      output = {
        "event_record_id": record["event_record_id"],
        "timestamp": record["timestamp"],
        "raw": record["data"]
      }

      output["data"]=Knead(output["raw"], parse_as = "xml").data()

      if file and (args.format == "json" or args.format == 'csv'):
        if args.format == 'csv':
          del output["raw"]
        file.write(json.dumps(output, indent=4))

      else:
        print(json.dumps(output, indent=4))



  if (args.format == 'json' or args.format == 'csv') and file:
    file.write("\n]")
    file.close()

  if args.format == 'csv':
    Knead("temp.json").write(args.output, write_as="csv")


  print(f"[+] Parsing completed. Total entries: {i}")
  print(f"[+] Time taken: {datetime.now()-t0}")


if __name__ == "__main__":
  main()
