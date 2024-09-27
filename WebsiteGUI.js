import React, { Component } from 'react';
import { AppRegistry, View, Text } from 'react-native';

class App extends Component {
  render() {
    return (
      <View>
        <Text>Hello, world!</Text>
      </View>
    );
  }
}

AppRegistry.registerComponent('App', () => App);