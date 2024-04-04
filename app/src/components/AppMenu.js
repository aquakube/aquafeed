import React from 'react';

import {
  IconButton,
  Menu,
  MenuList,
  MenuItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';

import { Link } from 'react-router-dom';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import HomeIcon from '@mui/icons-material/Home';
import SettingsIcon from '@mui/icons-material/Settings';
import InsightsIcon from '@mui/icons-material/Insights';

export default class AppMenu extends React.PureComponent {

  constructor(props) {
    super(props);

    this.state = {
      anchorEl: null,
      open: false,
    };
    this.open = Boolean(this.state.anchorEl);
  }

  componentDidMount() {}

  render() {
    const { anchorEl, open } = this.state;

    return (
      <div className=''>
        <IconButton
          id="long-button"
          onClick={(event) => this.setState({ anchorEl: event.currentTarget, open: true})}
        >
          <MoreVertIcon />
        </IconButton>
        <Menu
          id="long-menu"
          anchorEl={anchorEl}
          open={open}
          onClose={(event) => this.setState({ anchorEl: null, open: false })}
          slotProps={{
            paper: {
              style: {
                maxHeight: 48 * 4.5,
                width: '20ch',
              },
            }
          }}
        >
          <MenuList>
            <MenuItem onClick={(event) => this.setState({ anchorEl: null, open: false })} component={Link}  to="/">
              <ListItemIcon>
                <HomeIcon />
              </ListItemIcon>
              <ListItemText> Home </ListItemText>
            </MenuItem>
            <MenuItem onClick={(event) => this.setState({ anchorEl: null, open: false })} component={Link}  to="/advanced">
              <ListItemIcon>
                <InsightsIcon />
              </ListItemIcon>
              <ListItemText> Advanced </ListItemText>
            </MenuItem>
            <MenuItem onClick={(event) => this.setState({ anchorEl: null, open: false })} component={Link}  to="/specs">
              <ListItemIcon>
                <SettingsIcon />
              </ListItemIcon>
              <ListItemText> Specs </ListItemText>
            </MenuItem>
          </MenuList>
        </Menu>
      </div>
    );
  }
}




