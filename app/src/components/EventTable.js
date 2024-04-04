import * as React from 'react';

import { TableVirtuoso } from 'react-virtuoso';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';

import EventDialog from './EventDialog';
import EventStatus from './EventStatus';

const columns = [
  {
    width: '20%',
    label: 'Timestamp',
    dataKey: 'timestamp',
  },
  {
    width: '30%',
    label: 'Event',
    dataKey: 'event',
  },
  {
    width: '50%',
    label: 'Message',
    dataKey: 'message',
  },
];

function fixedHeaderContent() {
  return (
    <TableRow>
      {columns.map((column) => (
        <TableCell
          key={column.dataKey}
          variant="head"
          align={column.numeric || false ? 'right' : 'left'}
          style={{ width: column.width }}
          sx={{
            backgroundColor: 'background.paper',
          }}
        >
          {column.label}
        </TableCell>
      ))}
    </TableRow>
  );
}

function getComponents(self) {
  return {
    Scroller: React.forwardRef((props, ref) => (
      <TableContainer component={Paper} {...props} ref={ref} />
    )),
    Table: (props) => (
      <Table {...props} size={'small'} sx={{ borderCollapse: 'separate', tableLayout: 'fixed' }} />
    ),
    TableHead,
    TableRow: ({ item: _item, ...props }) => {
      let className = 'eventtablerow';
      if (_item.active) {
        className += ' eventtablerow--active';
      }
      return (
        <TableRow
          {...props}
          className={className}
          onClick={() => {
            self.setState({
              open: true,
              selectedEvent: self.props.events[props['data-index']]
            });
          }}
        >
          <TableCell>
            {_item.timestamp}
          </TableCell>
          <TableCell>
            <EventStatus event={_item.eventType} level={_item.level} />
          </TableCell>
          <TableCell>
            {_item.message}
          </TableCell>
        </TableRow>
      )
    },
    TableBody: React.forwardRef((props, ref) => <TableBody {...props} ref={ref} />),
  }
}

function makeRow(event, index) {
  return {
    index,
    timestamp: new Date(event.context.timestamp).toLocaleString(), //.toLocaleTimeString(),
    eventType: event.data.event,
    message: event.data.message,
    level: event.data.level,
  };
}

export default class EventsTable extends React.PureComponent {

  constructor(props) {
    super(props);

    this.state = {
      selectedEvent: null,
      open: false,
    };

    this.tableRef = React.createRef();
    this.components = getComponents(this);
  }

  componentDidMount() {
    window.addEventListener('resize', function() {
      console.debug("Firing table resizer");
      const windowHeight = window.innerHeight;
      const body = document.getElementsByClassName('body__automation')[0];
      if (!body) {
        return;
      }
      const navbarHeight = body.offsetHeight;
      const remainingSpace = windowHeight - navbarHeight - 48 - 16 - 16;
      document.querySelector('.eventtable').style.height = remainingSpace + 'px';
    });
    window.dispatchEvent(new Event('resize'));
  }

  render() {
    const { open, selectedEvent } = this.state;

    return (
      <div className="eventtable">
        <Paper>
          <TableVirtuoso
            ref={this.tableRef}
            data={this.props.events.map(makeRow)}
            fixedHeaderContent={fixedHeaderContent}
            components={this.components}
          />
          <EventDialog
            open={open}
            event={selectedEvent}
            onClose={() => this.setState({ open: false })}
          />
        </Paper>
      </div>
    );
  }

}