<?php

$config = array(

    'admin' => array(
        'core:AdminPassword',
    ),

    'example-userpass' => array(
        'exampleauth:UserPass',
        'user1:user1pass' => array(
            'mail' => 'user1@example.com',
        ),
        'user2:user2pass' => array(
            'mail' => 'user2@example.com',
        ),
    ),
);
