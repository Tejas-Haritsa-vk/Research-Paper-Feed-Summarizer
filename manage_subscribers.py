
import argparse
import sys
from utils.subscriber_manager import SubscriberManager

def main():
    parser = argparse.ArgumentParser(description="Manage subscribers for the Research Paper Agent.")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Add Command
    add_parser = subparsers.add_parser("add", help="Add a new subscriber")
    add_parser.add_argument("email", help="Email address of the subscriber")
    add_parser.add_argument("--topics", nargs="+", default=["AI", "Deep Learning"], help="List of topics of interest")

    # Remove Command
    remove_parser = subparsers.add_parser("remove", help="Remove a subscriber")
    remove_parser.add_argument("email", help="Email address to remove")

    # List Command
    subparsers.add_parser("list", help="List all active subscribers")
    
    # Update Topics Command
    update_parser = subparsers.add_parser("update", help="Update topics for a subscriber")
    update_parser.add_argument("email", help="Email address of the subscriber")
    update_parser.add_argument("topics", nargs="+", help="New list of topics")

    args = parser.parse_args()
    
    manager = SubscriberManager()

    if args.command == "add":
        if manager.add_subscriber(args.email, args.topics):
            print(f"[SUCCESS] Successfully added {args.email} with topics: {args.topics}")
        else:
            print(f"[ERROR] Failed to add {args.email}")

    elif args.command == "remove":
        manager.remove_subscriber(args.email)
        print(f"[SUCCESS] Removed {args.email} (if existed)")

    elif args.command == "list":
        subs = manager.get_active_subscribers()
        if not subs:
            print("No active subscribers found.")
        else:
            print(f"Found {len(subs)} active subscribers:")
            print("-" * 50)
            print(f"{'Email':<30} | {'Joined':<12} | {'Topics'}")
            print("-" * 50)
            for sub in subs:
                topics_str = ", ".join(sub['topics'])
                joined = sub['joined_date'].split('T')[0]
                print(f"{sub['email']:<30} | {joined:<12} | {topics_str}")

    elif args.command == "update":
        manager.update_topics(args.email, args.topics)
        print(f"[SUCCESS] Updated topics for {args.email} to: {args.topics}")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
