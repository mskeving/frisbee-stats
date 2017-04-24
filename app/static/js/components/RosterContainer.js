import React, { Component, PropTypes } from 'react';


export class Player extends Component {
  static propTypes = {
    player: PropTypes.object,
  }

  render() {
    return (
      <div className="player">
        {this.props.player}
      </div>
    );
  }
}


export class RosterContainer extends Component {

  render() {
    const player = { name: 'melissa skevington' };
    return (
      <div className="roster-container">
        <Player player={player} />
      </div>
    );
  }
}
