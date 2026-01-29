#!/bin/bash

SERVICE_NAME="law-crawler-ui"

case "$1" in
    install)
        echo "📦 Installing service..."
        sudo cp law-crawler-ui.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable $SERVICE_NAME
        echo "✅ Service installed and enabled"
        echo ""
        echo "Next steps:"
        echo "  ./ui-service.sh start   # Start the service"
        ;;
    start)
        echo "🚀 Starting service..."
        sudo systemctl start $SERVICE_NAME
        sudo systemctl status $SERVICE_NAME --no-pager
        ;;
    stop)
        echo "⏹️  Stopping service..."
        sudo systemctl stop $SERVICE_NAME
        ;;
    restart)
        echo "🔄 Restarting service..."
        sudo systemctl restart $SERVICE_NAME
        sudo systemctl status $SERVICE_NAME --no-pager
        ;;
    status)
        sudo systemctl status $SERVICE_NAME
        ;;
    logs)
        echo "📋 Showing logs (Ctrl+C to exit)..."
        sudo journalctl -u $SERVICE_NAME -f
        ;;
    deploy)
        echo "🚀 Deploying and restarting service..."
        ./ui-deploy.sh
        echo ""
        echo "📦 Installing dependencies..."
        cd ~/law-crawler/ui
        uv sync
        cd -
        echo ""
        echo "🔄 Restarting service..."
        sudo systemctl restart $SERVICE_NAME
        echo ""
        sudo systemctl status $SERVICE_NAME --no-pager
        ;;
    *)
        echo "Law Crawler UI Service Manager"
        echo ""
        echo "Usage: $0 {install|start|stop|restart|status|logs|deploy}"
        echo ""
        echo "Commands:"
        echo "  install  - Install systemd service (first time only)"
        echo "  start    - Start the service"
        echo "  stop     - Stop the service"
        echo "  restart  - Restart the service"
        echo "  status   - Show service status"
        echo "  logs     - Show real-time logs"
        echo "  deploy   - Deploy files and restart service"
        exit 1
        ;;
esac

exit 0
