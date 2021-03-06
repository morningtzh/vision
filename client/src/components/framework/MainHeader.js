import React, { Component } from 'react';
import PropTypes from 'prop-types';

import { Row, Col, Button, Input, Icon, Avatar, Popover } from 'antd';

import { observer } from "mobx-react";
import { autorun, computed, reaction } from "mobx";

import LoginPopover from '../modals/LoginPopover';

import modalControl from '../../funcs/modalcontroller';
import util from '../../funcs/util';


import icon from '../../../public/logo.png';

const Search = Input.Search;


@observer
class MainHeader extends Component {
    constructor(props) {
        super(props);
    }

    componentWillMount() {

    }

    componentDidMount() {

    }

    componentWillReceiveProps(nextProps) {

    }

    shouldComponentUpdate(nextProps, nextState) {

    }

    componentWillUpdate(nextProps, nextState) {

    }

    componentDidUpdate(prevProps, prevState) {

    }

    componentWillUnmount() {

    }

    render() {
        return (
            <div style={{ width: 1200, height: 48, margin: 'auto' }}>
                <Row style={{ height: 48, color: '#1DA1F2' }}>
                    <Col span={2} style={{ height: 48 }}>
                        <Icon type="home"/>主页
                    </Col>
                    <Col span={2} style={{ height: 48 }}>
                        {/* 杂文 */}
                    </Col>
                    <Col span={2} style={{ height: 48 }}>
                        {/* 瞬间 */}
                    </Col>
                    <Col span={4}/>
                    <Col span={6} style={{ height: 48 }}>
                        <Popover content={(<LoginPopover />)} trigger="click">
                            <Avatar src={icon}/>
                        </Popover>
                    </Col>
                    <Col span={3} style={{ height: 48 }}>
                        {/* <Search
                            placeholder="input search text"
                            onSearch={value => console.log(value)}
                        /> */}
                    </Col>
                    <Col span={5} style={{ height: 48 }}>
                        {
                            util.ifLogin ?

                                (<Button onClick={() => {
                                    modalControl.setModal('editer', null);
                                }}
                                ><Icon type="edit"/>
                                </Button>) :
                                null
                        }
                    </Col>
                </Row>
            </div>
        );
    }
}

MainHeader.propTypes = {};

export default MainHeader;
