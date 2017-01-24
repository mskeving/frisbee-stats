import React, { Component, PropTypes } from 'react';
import { Link } from 'react-router';

export class TopNav extends Component {
  render() {
    return (
      <div className="topNav">
        <Link to="/">Home</Link>
      </div>
    );
  }
}

export class PageContainer extends Component {
  static propTypes = {
    children: PropTypes.object,
  }

  render() {
    return (
      <div className="page">
        <TopNav />
        {this.props.children}
      </div>
    );
  }
}
