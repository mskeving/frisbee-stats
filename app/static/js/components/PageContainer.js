import React, { Component, PropTypes } from 'react';

export class CustomComponent extends Component {
  static propTypes = {
    message: PropTypes.string,
  }

  render() {
    const { message } = this.props;

    return <div>{ message }</div>;
  }
}

export class PageContainer extends Component {
  render() {
    return (
      <div>
        <CustomComponent message="Classy Ultimate" />
      </div>
    );
  }
}
